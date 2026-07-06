# altera-rag

An MCP (Model Context Protocol) server that provides Cursor and other AI coding assistants with semantic search over your private codebases, local files, hardware specs, and documentation. Built on [Crawl4AI](https://crawl4ai.com) for web content and custom indexing pipelines for code and file sources.

Embeddings run locally via **Ollama** - no data leaves your network.

---

## Features

- **Private repository indexing**: Clone and index internal Git repos (with `.netrc` / SSH key auth)
- **Local file indexing**: Index files directly from the server filesystem
- **Remote file indexing**: SCP files from other machines and index them
- **Web crawling**: Crawl public documentation sites and store them as searchable content
- **Cursor machine upload**: Upload files from your Windows/Linux laptop to the server for indexing
- **PDF and DOCX support**: Index hardware datasheets and Word documents (including embedded images inside them)
- **Image support**: Index standalone images and images embedded in PDFs/DOCX — OCR for text/tables/screenshots, vision LLM (llava) for block diagrams
- **Hardware file support**: `.rdl`, `.ralf`, `.csv`, `.xml`, and all standard source file types
- **No file size limit**: Configurable via `MAX_FILE_BYTES` (default: unlimited)
- **Incremental indexing**: `skip_existing` flag to only index new files
- **Local embeddings**: Ollama `mxbai-embed-large` (1024 dimensions) - no OpenAI key needed
- **Self-hosted database**: Works with self-hosted Supabase (Docker Compose)
- **Persistent Docker deployment**: Runs as a container on a Linux server, accessed via SSH tunnel from Cursor

---

## Architecture

```
Cursor (Windows) --SSH tunnel--> Linux Server
                                 +-- altera-rag container  (port 8051)
                                 +-- Supabase containers   (PostgreSQL + pgvector)
                                 +-- Ollama                (embeddings + LLM)
```

---

## Tools

### Web Crawling
| Tool | Description |
|------|-------------|
| `crawl_single_page` | Crawl a single URL and store content |
| `smart_crawl_url` | Auto-detect URL type (sitemap, text file, webpage) and crawl recursively |
| `get_available_sources` | List all crawled domains in the database |

### Repository & File Indexing
| Tool | Description |
|------|-------------|
| `index_repository_source` | Clone a Git repo and index all source files |
| `update_repository` | Re-index a previously indexed repo by name (uses stored URL) |
| `list_indexed_repositories` | List all indexed repos (Supabase + Neo4j) |
| `index_local_path` | Index files from a local path on the server |
| `index_remote_path` | SCP files from a remote machine and index them |
| `prepare_cursor_machine_upload` | Get SCP command to push files from your laptop to the server |

### Search & Retrieval
| Tool | Description |
|------|-------------|
| `perform_rag_query` | Semantic search over crawled web content |
| `search_repository_code` | Semantic search over indexed source files |
| `search_code_examples` | Search extracted code blocks (requires `USE_AGENTIC_RAG=true`) |
| `get_repository_file` | Retrieve a previously indexed file by repo + path |
| `gather_task_context` | Unified context bundle for a task: semantic snippets + symbol matches |
| `find_symbol_across_repos` | Find class/method/function by name across all repos (requires `USE_KNOWLEDGE_GRAPH=true`) |
| `resolve_include_chain` | Trace transitive `#include` dependencies of a C/C++ file across all indexed repos |

### Knowledge Graph (Optional)
| Tool | Description |
|------|-------------|
| `parse_github_repository` | Parse a repo into Neo4j for structural analysis |
| `check_ai_script_hallucinations` | Validate AI-generated code against the knowledge graph |
| `query_knowledge_graph` | Command-based Neo4j explorer (`repos`, `explore`, `classes`, `class`, `method`, `query`) |

Tool count in current server implementation: **19 MCP tools**.

Tool gating flags:
- `USE_AGENTIC_RAG=true` is required for `search_code_examples`.
- `USE_KNOWLEDGE_GRAPH=true` is required for `parse_github_repository`, `check_ai_script_hallucinations`, `query_knowledge_graph`, and `find_symbol_across_repos`.

---

## Deployment

### Prerequisites

- Linux server with Docker installed
- [Ollama](https://ollama.com/) running on the server with `mxbai-embed-large` pulled
- For image support: pull `llava` model — `ollama pull llava`
- Self-hosted Supabase (Docker Compose) or a cloud Supabase project

### 1. Clone the repository on the server

```bash
git clone <this-repo-url>
cd mcp-crawl4ai-rag
```

### 2. Set up the database

Run the SQL schema against your Supabase PostgreSQL instance:

```bash
docker exec -it supabase-db psql -U postgres -d postgres -f /path/to/crawled_pages.sql
```

Or paste the contents of `crawled_pages.sql` into the Supabase SQL editor.

If upgrading from a previous version, add the metadata column:

```sql
ALTER TABLE sources ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
```

### 3. Create `.env`

```env
# Server
HOST=0.0.0.0
PORT=8051
TRANSPORT=streamable-http

# Ollama embeddings (no OpenAI key needed)
EMBEDDING_BASE_URL=http://localhost:11434/v1
EMBEDDING_MODEL=mxbai-embed-large
EMBEDDING_DIMENSIONS=1024
EMBEDDING_MAX_CHARS=1800
EMBEDDING_PARALLEL_BATCHES=32
OPENAI_API_KEY=ollama

# LLM (only used when USE_CONTEXTUAL_EMBEDDINGS=true)
MODEL_CHOICE=llama3.2

# RAG strategies
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false

# Supabase (self-hosted uses http://localhost:8000, cloud uses your project URL)
SUPABASE_URL=http://localhost:8000
SUPABASE_SERVICE_KEY=<your-service-role-key>

# Chunking
CHUNK_SIZE=1500
MAX_FILE_BYTES=0

# Remote systems config (for index_remote_path)
REMOTE_SYSTEMS_CONFIG=/app/remote_systems.json

# SSH info for prepare_cursor_machine_upload (server own SSH details)
SERVER_SSH_HOST=<server IP>
SERVER_SSH_USER=<your-username>
SERVER_SSH_PORT=22
SERVER_SSH_PASSWORD=<password>   # or use SERVER_SSH_KEY=/path/to/key

# Image processing (requires rebuild for OCR)
USE_IMAGE_OCR=true             # OCR via Tesseract — best for text/tables/screenshots
USE_IMAGE_VISION=true          # llava vision LLM — best for block diagrams
VISION_MODEL=llava
IMAGE_OCR_MIN_CHARS=50         # if OCR finds fewer chars than this, also run vision
```

### 4. Build the Docker image

```bash
docker build -t altera-rag --build-arg PORT=8051 .
```

### 5. Run the container

```bash
docker run -d \
  --name altera-rag \
  --env-file .env \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/src:/app/src \
  -v /home/<user>:/home/<user>:ro \
  -v /home/<user>/.netrc:/root/.netrc:ro \
  -v /home/<user>/.ssh:/root/.ssh:ro \
  -v /home/<user>/.gitconfig:/root/.gitconfig:ro \
  -v $(pwd)/remote_systems.json:/app/remote_systems.json:rw \
  altera-rag
```

> The `src` volume mount means you can update code by copying a file and running `docker restart altera-rag` without rebuilding the image.

### 6. Verify

```bash
docker logs -f altera-rag
# Expect: Uvicorn running on http://0.0.0.0:8051
```

---

## Connecting Cursor

### Open an SSH tunnel (keep this terminal open)

```bash
ssh -L 8051:localhost:8051 <user>@<SERVER_IP>
```

### Configure Cursor (`mcp.json`)

```json
{
  "mcpServers": {
    "altera-rag": {
      "url": "http://localhost:8051/mcp",
      "timeout": 7200
    }
  }
}
```

---

## Indexing Scenarios

### Index a Git repository (private or public)

```
index_repository_source("https://github.com/my-org/my-repo.git")
```

To refresh an already indexed repository by name:

```
update_repository(repo_name="my-repo")
```

For private repos, ensure `.netrc` or SSH keys are mounted into the container (see step 5 above).

### Index local files on the server

```
index_local_path(local_path="/home/user/specs/chip_registers", source_name="vsip-registers")
```

### Index files from your laptop (Cursor machine)

```
prepare_cursor_machine_upload(source_name="my-specs")
# Returns an scp command - run it in your local terminal, then:
# Returns an scp command - run it in your local terminal, then:
index_local_path(local_path="<returned staging_path>", source_name="my-specs")
```

### Index files from another machine via SCP

```
index_remote_path(
    remote_path="/home/user/projects/chiplib",
    source_name="chiplib",
    host="192.168.1.50",
    user="engineer",
    password="secret",
    save_credentials=True,
    system_name="dev-server"
)
```

Next time, just use `system_name="dev-server"` - credentials are saved in `remote_systems.json`.

### Crawl a documentation website

```
smart_crawl_url("https://docs.example.com/sitemap.xml")
```

### Explore the knowledge graph

```
query_knowledge_graph("repos")
query_knowledge_graph("explore my-repo")
query_knowledge_graph("classes my-repo")
```

---

## Supported File Types

| Category | Extensions |
|----------|-----------|
| Python | `.py` |
| C/C++ | `.c`, `.cpp`, `.h`, `.hpp`, `.cc`, `.cxx` |
| SystemRDL | `.rdl`, `.ralf` |
| Web | `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css` |
| Data | `.csv`, `.tsv`, `.txt`, `.xml`, `.json`, `.yaml`, `.yml` |
| Docs | `.md`, `.rst`, `.pdf`, `.docx` |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`, `.webp` |
| Other | `.java`, `.rs`, `.go`, `.rb`, `.sh`, `.sv`, `.v`, `.vhd` |

---

## Updating Code (without rebuilding)

Since `src/` is volume-mounted:

```bash
# On Windows - copy updated file to server
scp src\altera_rag.py user@SERVER:/path/to/RAG_MCP/src/altera_rag.py

# On server - restart the container
docker restart altera-rag
```

Only rebuild the image when `pyproject.toml` or `Dockerfile` changes.

---

## Managing the Container

```bash
docker stop altera-rag      # Stop (will not auto-restart)
docker start altera-rag     # Start again
docker restart altera-rag   # Restart
docker logs -f altera-rag   # Tail logs
```

---

## RAG Strategy Options

All strategies default to `false`. Enable in `.env`:

| Variable | Description |
|----------|-------------|
| `USE_CONTEXTUAL_EMBEDDINGS` | Enrich chunks with full-document context via LLM before embedding. Slower indexing, better retrieval. |
| `USE_HYBRID_SEARCH` | Combine vector search with keyword search. Better for exact term matches. |
| `USE_AGENTIC_RAG` | Extract and store code blocks separately. Enables `search_code_examples`. |
| `USE_RERANKING` | Re-rank search results with a cross-encoder. Better result ordering, no extra API cost. |
| `USE_KNOWLEDGE_GRAPH` | Enable Neo4j-based structural analysis and hallucination detection. Requires Neo4j. |

## Image Processing Options

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_IMAGE_OCR` | `false` | Tesseract OCR for images. Best for text, tables, terminal screenshots, scanned docs. Requires rebuild. |
| `USE_IMAGE_VISION` | `false` | llava vision LLM for images. Best for block diagrams and architecture drawings. |
| `VISION_MODEL` | `llava` | Ollama vision model to use. |
| `IMAGE_OCR_MIN_CHARS` | `50` | If OCR returns fewer chars than this, also run vision LLM as fallback. |

Image processing is applied to:
- Standalone image files (`.png`, `.jpg`, etc.)
- Images embedded inside `.pdf` files
- Images embedded inside `.docx` files

## Ollama Load Settings

Start Ollama with settings tuned for your server before running the container:

```bash
# Stop existing Ollama instance
sudo systemctl stop ollama 2>/dev/null || sudo lsof -ti:11434 | xargs sudo kill -9
sleep 2

# Start with parallel processing enabled
# Tune OLLAMA_NUM_THREAD to ~70% of your cores
OLLAMA_NUM_PARALLEL=36 \
OLLAMA_NUM_THREAD=80 \
OLLAMA_MAX_LOADED_MODELS=2 \
ollama serve &
```

| Setting | Recommended (112-core server) | Description |
|---------|-------------------------------|-------------|
| `OLLAMA_NUM_PARALLEL` | `36` | Concurrent requests (embedding + vision combined) |
| `OLLAMA_NUM_THREAD` | `80` | CPU threads (~70% of cores, leaves headroom for OS) |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | Keep `mxbai-embed-large` + `llava` both hot in memory |

Verify Ollama is running:
```bash
ss -tlnp | grep 11434
curl -s http://localhost:11434/api/version
```

---

## Knowledge Graph Setup (Optional)

Requires Neo4j. Set `USE_KNOWLEDGE_GRAPH=true` and add to `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

> Note: Knowledge graph features currently work best when running outside Docker (directly via `uv run src/altera_rag.py`).

---

## Remote Systems Config

Save SSH credentials for remote machines in `remote_systems.json`:

```json
{
  "dev-server": {
    "host": "192.168.1.50",
    "user": "engineer",
    "port": 22,
    "ssh_key": "/root/.ssh/id_rsa"
  },
  "build-server": {
    "host": "192.168.1.51",
    "user": "build",
    "port": 22,
    "password": "secret"
  }
}
```

Use either `ssh_key` (path to key on the server) or `password` - not both.
