"""
Cross-repository code context utilities.

This module gives the MCP agent practical access to the context of *all*
indexed code repositories. It complements the existing single-repo Neo4j
ingestion (``parse_github_repository``) and the page-oriented Supabase
RAG store with:

  * Cross-repo source file indexing into Supabase (``type=repo_file``)
  * Cross-repo semantic search over indexed source files
  * Cross-repo symbol lookup (class / method / function) using Neo4j
  * File-content reconstruction by repo + path
  * A unified ``gather_task_context`` helper that combines semantic
    snippets, symbol matches and repo metadata for a free-text task.

The functions here intentionally reuse the existing Supabase schema
(``crawled_pages`` / ``sources``) rather than introducing new tables, so
no migration is required. Indexed source files are stored with:

  * ``url``        = ``repo://<repo_name>/<relative_path>``
  * ``source_id``  = ``repo:<repo_name>``
  * ``metadata``   includes ``{"type": "repo_file", "repo_name": ...,
    "path": ..., "language": ..., "branch": ...}``

This makes it easy to filter cross-repo source content from regular
crawled documentation pages.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from supabase import Client

from utils import (
    add_documents_to_supabase,
    create_embedding,
    update_source_info,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# File extensions we treat as "source code" worth indexing for context.
# Kept conservative to avoid blowing up the embedding bill on huge repos.
SOURCE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".sql": "sql",
    ".md": "markdown",
    ".rst": "rst",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".json": "json",
}

EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    "build", "dist", ".pytest_cache", ".mypy_cache", ".tox",
    "target", "out", ".next", ".nuxt", ".cache", ".idea", ".vscode",
}

MAX_FILE_BYTES = 200_000          # skip very large files
DEFAULT_CHUNK_CHARS = 4_000       # chars per code chunk
DEFAULT_CHUNK_OVERLAP = 200       # overlap between consecutive chunks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_repo_name(repo_url: str) -> str:
    """Derive a stable repo name from a git URL."""
    name = repo_url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def repo_source_id(repo_name: str) -> str:
    """Source-id namespace used for indexed repo source files."""
    return f"repo:{repo_name}"


def repo_file_url(repo_name: str, relative_path: str) -> str:
    """Synthetic URL used to identify an indexed source file."""
    rel = relative_path.replace("\\", "/").lstrip("/")
    return f"repo://{repo_name}/{rel}"


def _iter_source_files(repo_root: Path) -> Iterable[Path]:
    """Walk a cloned repo and yield candidate source files."""
    for root, dirs, files in os.walk(repo_root):
        # Prune excluded / hidden dirs in-place
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SOURCE_EXTENSIONS:
                continue
            fpath = Path(root) / fname
            try:
                if fpath.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield fpath


def _chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_CHARS,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Simple character-based chunking with overlap, line-aware where possible."""
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # try to break on the nearest preceding newline for cleaner chunks
        if end < n:
            nl = text.rfind("\n", start + int(chunk_size * 0.6), end)
            if nl != -1 and nl > start:
                end = nl + 1
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def _clone_repo(repo_url: str, target_dir: str) -> Path:
    """Shallow clone a repo into target_dir. Removes target_dir first if needed."""
    if os.path.exists(target_dir):
        def _onerr(func, path, _exc):
            try:
                if os.path.exists(path):
                    os.chmod(path, 0o777)
                    func(path)
            except OSError:
                pass
        shutil.rmtree(target_dir, onerror=_onerr)

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, target_dir],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return Path(target_dir)


def _get_default_branch(repo_path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True, capture_output=True, text=True,
        )
        return out.stdout.strip() or "HEAD"
    except Exception:
        return "HEAD"


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def index_repository_source_files(
    supabase_client: Client,
    repo_url: str,
    temp_dir: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_CHARS,
    max_files: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Clone ``repo_url`` and index its source files into Supabase so they can
    be semantically searched across all repositories.

    Stored rows live in ``crawled_pages`` with ``source_id = repo:<name>``
    and ``metadata.type = "repo_file"``. A matching row is also upserted
    into the ``sources`` table so the repo shows up in ``list_indexed_repositories``.

    Returns a summary dict with counts.
    """
    repo_name = _safe_repo_name(repo_url)
    src_id = repo_source_id(repo_name)

    cleanup = False
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp(prefix=f"repoctx-{repo_name}-")
        cleanup = True

    try:
        repo_path = _clone_repo(repo_url, temp_dir)
        branch = _get_default_branch(repo_path)

        urls: List[str] = []
        chunk_numbers: List[int] = []
        contents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        url_to_full_document: Dict[str, str] = {}

        files_indexed = 0
        total_chars = 0

        for fpath in _iter_source_files(repo_path):
            if max_files is not None and files_indexed >= max_files:
                break

            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not text.strip():
                continue

            rel_path = str(fpath.relative_to(repo_path)).replace("\\", "/")
            ext = fpath.suffix.lower()
            language = SOURCE_EXTENSIONS.get(ext, "text")
            url = repo_file_url(repo_name, rel_path)

            chunks = _chunk_text(text, chunk_size=chunk_size)
            url_to_full_document[url] = text

            for idx, chunk in enumerate(chunks):
                urls.append(url)
                chunk_numbers.append(idx)
                contents.append(chunk)
                metadatas.append({
                    "type": "repo_file",
                    "repo_name": repo_name,
                    "path": rel_path,
                    "language": language,
                    "branch": branch,
                    "chunk_index": idx,
                    "chunk_total": len(chunks),
                    "source": src_id,
                })

            files_indexed += 1
            total_chars += len(text)

        # Ensure sources row exists so the repo appears in source listings.
        summary = (
            f"Indexed source files from GitHub repository '{repo_name}' "
            f"({files_indexed} files, {total_chars} chars). "
            f"Use search_repository_code or gather_task_context to query."
        )
        try:
            update_source_info(
                supabase_client, src_id, summary, total_chars
            )
        except Exception as e:  # pragma: no cover - non-fatal
            print(f"[repo_context] update_source_info failed for {src_id}: {e}")

        if contents:
            add_documents_to_supabase(
                supabase_client,
                urls,
                chunk_numbers,
                contents,
                metadatas,
                url_to_full_document,
            )

        return {
            "repo_name": repo_name,
            "source_id": src_id,
            "branch": branch,
            "files_indexed": files_indexed,
            "chunks_indexed": len(contents),
            "total_chars": total_chars,
        }
    finally:
        if cleanup and os.path.exists(temp_dir):
            def _onerr(func, path, _exc):
                try:
                    if os.path.exists(path):
                        os.chmod(path, 0o777)
                        func(path)
                except OSError:
                    pass
            try:
                shutil.rmtree(temp_dir, onerror=_onerr)
            except Exception:  # pragma: no cover
                pass


# ---------------------------------------------------------------------------
# Listing & retrieval
# ---------------------------------------------------------------------------

def list_indexed_repositories(
    supabase_client: Client,
    neo4j_driver: Any = None,
) -> Dict[str, Any]:
    """
    Return all repositories the agent has context for, combining:
      * Supabase ``sources`` rows whose id starts with ``repo:`` (semantic store)
      * Neo4j ``Repository`` nodes (structural / knowledge-graph store)
    """
    semantic_repos: Dict[str, Dict[str, Any]] = {}
    try:
        res = supabase_client.table("sources").select(
            "source_id, summary, total_word_count, updated_at"
        ).like("source_id", "repo:%").execute()
        for row in res.data or []:
            name = row["source_id"].split(":", 1)[1]
            semantic_repos[name] = {
                "repo_name": name,
                "source_id": row["source_id"],
                "summary": row.get("summary"),
                "total_chars": row.get("total_word_count"),
                "updated_at": row.get("updated_at"),
                "in_semantic_store": True,
                "in_knowledge_graph": False,
            }
    except Exception as e:  # pragma: no cover - DB might not be configured
        print(f"[repo_context] list semantic repos failed: {e}")

    if neo4j_driver is not None:
        try:
            kg_repos = _list_kg_repos_sync(neo4j_driver)
            for name in kg_repos:
                if name in semantic_repos:
                    semantic_repos[name]["in_knowledge_graph"] = True
                else:
                    semantic_repos[name] = {
                        "repo_name": name,
                        "source_id": repo_source_id(name),
                        "summary": None,
                        "total_chars": None,
                        "updated_at": None,
                        "in_semantic_store": False,
                        "in_knowledge_graph": True,
                    }
        except Exception as e:
            print(f"[repo_context] list KG repos failed: {e}")

    repos = sorted(semantic_repos.values(), key=lambda r: r["repo_name"])
    return {"count": len(repos), "repositories": repos}


async def list_indexed_repositories_async(
    supabase_client: Client,
    neo4j_driver: Any = None,
) -> Dict[str, Any]:
    """Async version using Neo4j async driver."""
    result = list_indexed_repositories(supabase_client, neo4j_driver=None)
    if neo4j_driver is None:
        return result

    by_name = {r["repo_name"]: r for r in result["repositories"]}
    try:
        async with neo4j_driver.session() as session:
            res = await session.run("MATCH (r:Repository) RETURN r.name AS name")
            records = await res.data()
            for rec in records:
                name = rec["name"]
                if name in by_name:
                    by_name[name]["in_knowledge_graph"] = True
                else:
                    by_name[name] = {
                        "repo_name": name,
                        "source_id": repo_source_id(name),
                        "summary": None,
                        "total_chars": None,
                        "updated_at": None,
                        "in_semantic_store": False,
                        "in_knowledge_graph": True,
                    }
    except Exception as e:
        print(f"[repo_context] list KG repos (async) failed: {e}")

    repos = sorted(by_name.values(), key=lambda r: r["repo_name"])
    return {"count": len(repos), "repositories": repos}


def _list_kg_repos_sync(driver: Any) -> List[str]:
    """Best-effort sync listing of KG repos (used only for non-async drivers)."""
    try:
        with driver.session() as session:
            res = session.run("MATCH (r:Repository) RETURN r.name AS name")
            return [rec["name"] for rec in res]
    except Exception:
        return []


def search_repository_code(
    supabase_client: Client,
    query: str,
    repo_name: Optional[str] = None,
    match_count: int = 10,
) -> List[Dict[str, Any]]:
    """
    Semantic search over indexed repository source files.

    If ``repo_name`` is provided, results are restricted to that repo.
    Otherwise the search runs across *all* indexed repos so the agent can
    pull context from every code source it knows about.
    """
    if not query or not query.strip():
        return []

    embedding = create_embedding(query)
    params: Dict[str, Any] = {
        "query_embedding": embedding,
        "match_count": match_count,
        "filter": {"type": "repo_file"},
    }
    if repo_name:
        params["source_filter"] = repo_source_id(repo_name)

    try:
        res = supabase_client.rpc("match_crawled_pages", params).execute()
        rows = res.data or []
    except Exception as e:
        print(f"[repo_context] search_repository_code failed: {e}")
        return []

    out: List[Dict[str, Any]] = []
    for row in rows:
        meta = row.get("metadata") or {}
        out.append({
            "repo_name": meta.get("repo_name"),
            "path": meta.get("path"),
            "language": meta.get("language"),
            "branch": meta.get("branch"),
            "url": row.get("url"),
            "chunk_number": row.get("chunk_number"),
            "similarity": row.get("similarity"),
            "content": row.get("content"),
        })
    return out


def get_repository_file(
    supabase_client: Client,
    repo_name: str,
    path: str,
) -> Dict[str, Any]:
    """
    Reconstruct a previously indexed source file from its chunks in Supabase.
    """
    url = repo_file_url(repo_name, path)
    try:
        res = (
            supabase_client.table("crawled_pages")
            .select("chunk_number, content, metadata")
            .eq("url", url)
            .order("chunk_number")
            .execute()
        )
        rows = res.data or []
    except Exception as e:
        return {"found": False, "error": str(e)}

    if not rows:
        return {"found": False, "repo_name": repo_name, "path": path}

    # Reassemble using the same chunking logic (overlap-aware): if chunks
    # were created with overlap, reconcatenating with simple join would
    # duplicate content. We trim using stored chunk_total/chunk_index to
    # keep ordering, then de-duplicate overlap by trimming the leading
    # overlap region of every non-first chunk.
    pieces: List[str] = []
    for i, row in enumerate(rows):
        content = row.get("content") or ""
        if i == 0:
            pieces.append(content)
        else:
            # Best-effort overlap trim using DEFAULT_CHUNK_OVERLAP
            trim = min(DEFAULT_CHUNK_OVERLAP, len(content))
            pieces.append(content[trim:])

    full = "".join(pieces)
    meta = rows[0].get("metadata") or {}
    return {
        "found": True,
        "repo_name": repo_name,
        "path": path,
        "language": meta.get("language"),
        "branch": meta.get("branch"),
        "chunks": len(rows),
        "content": full,
    }


# ---------------------------------------------------------------------------
# Symbol search across all repos (Neo4j)
# ---------------------------------------------------------------------------

async def find_symbol_across_repos(
    neo4j_driver: Any,
    name: str,
    kind: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Find Class / Method / Function symbols whose name matches ``name``
    (case-insensitive substring) across *all* indexed repositories.

    ``kind`` may be one of ``"class"``, ``"method"``, ``"function"``, or
    ``None`` (search all three).
    """
    kinds = [kind.lower()] if kind else ["class", "method", "function"]
    results: List[Dict[str, Any]] = []
    needle = name.lower()

    async with neo4j_driver.session() as session:
        if "class" in kinds:
            q = """
            MATCH (r:Repository)-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
            WHERE toLower(c.name) CONTAINS $needle
               OR toLower(c.full_name) CONTAINS $needle
            RETURN r.name AS repo, f.path AS file, c.name AS name,
                   c.full_name AS full_name, 'class' AS kind
            LIMIT $limit
            """
            res = await session.run(q, needle=needle, limit=limit)
            results.extend(await res.data())

        if "method" in kinds:
            q = """
            MATCH (r:Repository)-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_METHOD]->(m:Method)
            WHERE toLower(m.name) CONTAINS $needle
            RETURN r.name AS repo, f.path AS file, m.name AS name,
                   c.full_name AS class_full_name,
                   m.params_list AS params, m.return_type AS return_type,
                   'method' AS kind
            LIMIT $limit
            """
            res = await session.run(q, needle=needle, limit=limit)
            results.extend(await res.data())

        if "function" in kinds:
            q = """
            MATCH (r:Repository)-[:CONTAINS]->(file:File)-[:DEFINES]->(func:Function)
            WHERE toLower(func.name) CONTAINS $needle
            RETURN r.name AS repo, file.path AS file, func.name AS name,
                   func.params_list AS params, func.return_type AS return_type,
                   'function' AS kind
            LIMIT $limit
            """
            res = await session.run(q, needle=needle, limit=limit)
            results.extend(await res.data())

    return results[:limit]


# ---------------------------------------------------------------------------
# Unified task-context assembly
# ---------------------------------------------------------------------------

async def gather_task_context(
    supabase_client: Client,
    neo4j_driver: Any,
    task: str,
    repo_name: Optional[str] = None,
    max_snippets: int = 8,
    max_symbols: int = 10,
) -> Dict[str, Any]:
    """
    Assemble a single, task-focused context bundle by combining:

      * Top-K semantic snippets from indexed repo source files
      * Symbol matches (class / method / function) from the knowledge graph
      * The list of repos contributing to the answer

    The result is intentionally small enough to fit into a model prompt
    while still spanning *all* indexed repositories the agent has access to.
    """
    snippets = search_repository_code(
        supabase_client, task, repo_name=repo_name, match_count=max_snippets
    )

    # Build a compact symbol query from the task: words that look like identifiers
    import re as _re
    candidate_terms = sorted(set(
        t for t in _re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", task or "")
    ), key=len, reverse=True)[:5]

    symbols: List[Dict[str, Any]] = []
    if neo4j_driver is not None and candidate_terms:
        seen: set = set()
        per_term = max(2, max_symbols // max(1, len(candidate_terms)))
        for term in candidate_terms:
            try:
                hits = await find_symbol_across_repos(
                    neo4j_driver, term, kind=None, limit=per_term
                )
            except Exception as e:
                print(f"[repo_context] symbol lookup failed for {term!r}: {e}")
                hits = []
            for h in hits:
                key = (h.get("repo"), h.get("kind"), h.get("name"),
                       h.get("file"), h.get("class_full_name"))
                if key in seen:
                    continue
                seen.add(key)
                symbols.append(h)
                if len(symbols) >= max_symbols:
                    break
            if len(symbols) >= max_symbols:
                break

    repos_used = sorted({s["repo_name"] for s in snippets if s.get("repo_name")} |
                        {s.get("repo") for s in symbols if s.get("repo")})

    return {
        "task": task,
        "repos_used": repos_used,
        "snippet_count": len(snippets),
        "symbol_count": len(symbols),
        "snippets": snippets,
        "symbols": symbols,
        "candidate_terms": candidate_terms,
    }
