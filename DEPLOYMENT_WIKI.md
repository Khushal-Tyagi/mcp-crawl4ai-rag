# MCP Crawl4AI RAG Server — Deployment Wiki

Complete guide to deploying the MCP server on a Linux office server and connecting Cursor IDE on a Windows laptop via SSH tunnel, using Ollama for local embeddings (no OpenAI API key required).

---

## Architecture Overview

```
Windows Laptop (Cursor IDE)
        |
        | SSH Tunnel (port 8051)
        |
Linux Server (112-core)
  ├── Docker: altera-rag  (port 8051, streamable-http)
  ├── Docker: Supabase           (port 8000, self-hosted)
  └── Ollama                     (port 11434, mxbai-embed-large)
```

- **MCP Server**: FastMCP with `streamable-http` transport, endpoint `/mcp`
- **Embeddings**: Ollama `mxbai-embed-large` (1024 dimensions) — no OpenAI needed
- **LLM for summaries**: `llama3.2` via Ollama (only if contextual embeddings enabled)
- **Database**: Self-hosted Supabase via Docker Compose
- **Transport**: `streamable-http` (required for Cursor's newer MCP client)

---

## Prerequisites (Linux Server)

- Docker + Docker Compose installed
- Ollama installed
- Git installed on the host (for credentials)
- Self-hosted Supabase running (see Supabase section below)

---

## 1. Self-Hosted Supabase Setup

If not already running:

```bash
git clone https://github.com/supabase/supabase
cd supabase/docker
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD, JWT_SECRET, ANON_KEY, SERVICE_ROLE_KEY
docker compose up -d
```

Supabase will be available at `http://localhost:8000`.

Get your `SERVICE_ROLE_KEY` from `supabase/docker/.env`.

---

## 2. Database Schema Setup

Run this once (or re-run after resetting):

```bash
docker exec -i supabase-db psql -U postgres -d postgres < /path/to/RAG_MCP/crawled_pages.sql
```

> **Note**: The schema uses `vector(1024)` for `mxbai-embed-large` embeddings.  
> If you previously ran with OpenAI's `text-embedding-3-small` (1536 dims), you must re-run the SQL to reset.

### DB Migration (if adding to existing DB without resetting)

If your DB already exists and you just need to add the `metadata` column to `sources`:

```bash
docker exec -it supabase-db psql -U postgres -d postgres -c \
  "ALTER TABLE sources ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;"
```

---

## 3. Ollama Setup

```bash
# Pull required models
ollama pull mxbai-embed-large   # embeddings (required)
ollama pull llama3.2            # LLM for summaries (only needed if USE_CONTEXTUAL_EMBEDDINGS=true)
ollama pull llava               # vision LLM for image indexing (only needed if USE_IMAGE_VISION=true)

# Stop any existing Ollama instance first
sudo systemctl stop ollama 2>/dev/null || sudo lsof -ti:11434 | xargs sudo kill -9 2>/dev/null
sleep 2

# Start Ollama with parallel processing tuned for 112-core server
OLLAMA_NUM_PARALLEL=36 \
OLLAMA_NUM_THREAD=80 \
OLLAMA_MAX_LOADED_MODELS=2 \
ollama serve &
```

| Setting | Value | Rationale |
|---------|-------|----------|
| `OLLAMA_NUM_PARALLEL` | 36 | Handles 32 embedding + 4 vision requests concurrently |
| `OLLAMA_NUM_THREAD` | 80 | ~70% of 112 cores — leaves headroom for OS and Docker |
| `OLLAMA_MAX_LOADED_MODELS` | 2 | Keeps both `mxbai-embed-large` and `llava` hot in memory |

Verify Ollama started:
```bash
jobs                              # check background process is Running
ss -tlnp | grep 11434             # port should be LISTEN
curl -s http://localhost:11434/api/version
```

---

## 4. Environment File (.env)

Create `/path/to/RAG_MCP/.env` on the server:

```env
HOST=0.0.0.0
PORT=8051
TRANSPORT=streamable-http

# Ollama settings
EMBEDDING_BASE_URL=http://localhost:11434/v1
EMBEDDING_MODEL=mxbai-embed-large
EMBEDDING_DIMENSIONS=1024
EMBEDDING_MAX_CHARS=1800
EMBEDDING_PARALLEL_BATCHES=32
OPENAI_API_KEY=ollama

# LLM (only used if USE_CONTEXTUAL_EMBEDDINGS=true)
MODEL_CHOICE=llama3.2

# Feature flags (keep all false unless you need them)
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false

# Supabase (self-hosted)
SUPABASE_URL=http://localhost:8000
SUPABASE_SERVICE_KEY=<your SERVICE_ROLE_KEY from supabase/docker/.env>

# Chunking
CHUNK_SIZE=1500

# Remote file indexing
REMOTE_SYSTEMS_CONFIG=/app/remote_systems.json
# Used when indexing files FROM your Cursor machine (Scenario 1)
SERVER_SSH_HOST=<this server's IP or hostname>
SERVER_SSH_USER=bapvesm013t
SERVER_SSH_PORT=22
SERVER_SSH_KEY=   # leave blank if using password/agent auth

# Image processing
USE_IMAGE_OCR=true             # Tesseract OCR (text, tables, screenshots)
USE_IMAGE_VISION=true          # llava vision LLM (block diagrams, architecture drawings)
VISION_MODEL=llava
IMAGE_OCR_MIN_CHARS=50         # fallback to vision if OCR finds fewer chars than this
```

---

## 5. Copy Files to Server

From your Windows machine (PowerShell):

```powershell
$SERVER = "bapvesm013t@<SERVER_IP>"
$REMOTE = "/home/bapvesm013t/khushal/RAG_MCP"

scp src\utils.py         "${SERVER}:${REMOTE}/src/utils.py"
scp src\altera_rag.py  "${SERVER}:${REMOTE}/src/altera_rag.py"
scp src\repo_context.py  "${SERVER}:${REMOTE}/src/repo_context.py"
scp crawled_pages.sql    "${SERVER}:${REMOTE}/crawled_pages.sql"
scp Dockerfile           "${SERVER}:${REMOTE}/Dockerfile"
scp pyproject.toml       "${SERVER}:${REMOTE}/pyproject.toml"
```

---

## 6. Build Docker Image

SSH into the server then:

```bash
cd /home/bapvesm013t/khushal/RAG_MCP

# Build (first time or after Dockerfile changes — takes ~10-15 min)
docker build -t altera-rag --build-arg PORT=8051 .

# Verify git is included
docker run --rm altera-rag git --version
# Expected: git version 2.x.x
```

> After the first full build, subsequent builds only rebuild changed layers:
> - Code-only changes (`src/`) → **seconds**
> - Dependency changes (`pyproject.toml`) → a few minutes
> - Base image / git layer → full rebuild (rare)

---

## 7. Git Credentials for Private Repos

The container needs access to your git credentials to clone private repositories.

**Check which method your server uses:**
```bash
cat ~/.gitconfig | grep helper
ls -la ~/.ssh/
cat ~/.netrc 2>/dev/null
```

| Credential Method | Mount Flag |
|---|---|
| `~/.netrc` file | `-v /home/user/.netrc:/root/.netrc:ro` |
| SSH keys (`~/.ssh/`) | `-v /home/user/.ssh:/root/.ssh:ro` |
| No file found | Use token in URL: `https://user:token@github.com/org/repo` |

---

## 8. Run the Docker Container

```bash
# Stop/remove old container if it exists
docker stop altera-rag 2>/dev/null
docker rm altera-rag 2>/dev/null

# Run (adjust credential mount based on section 7)
docker run -d \
  --name altera-rag \
  --env-file /home/bapvesm013t/khushal/RAG_MCP/.env \
  --network host \
  --restart unless-stopped \
  -v /home/bapvesm013t/.netrc:/root/.netrc:ro \
  altera-rag
```

**Check it's running:**
```bash
docker logs -f altera-rag
# Expected: Uvicorn running on http://0.0.0.0:8051
```

---

## 9. Connect Cursor IDE (Windows)

### Step 1 — Open SSH Tunnel (keep this terminal open)

```powershell
ssh -L 8051:localhost:8051 bapvesm013t@<SERVER_IP>
```

### Step 2 — Configure Cursor mcp.json

Location: `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json`  
or in your project: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "url": "http://localhost:8051/mcp",
      "timeout": 7200
    }
  }
}
```

### Step 3 — Verify in Cursor

In Cursor chat, ask: `list_indexed_repositories` — it should return an empty list (no error).

---

## 10. Indexing Repositories

### Index a new repo (from Cursor)

```
Call index_repository_source:
  repo_url: "https://github.com/org/repo"
  max_files: 0          ← 0 = no limit
  chunk_size: 4000
  force_reindex: false
```

For private repos with token in URL:
```
  repo_url: "https://username:ghp_yourtoken@github.com/org/private-repo"
```

### Re-index an existing repo (force fresh)

```
Call index_repository_source:
  repo_url: "https://github.com/org/repo"
  force_reindex: true
```

### Update a repo by name (no URL needed)

After the first index, the URL is stored. Future updates just need the name:

```
Call update_repository:
  repo_name: "repo"
```

### List all indexed repos

```
Call list_indexed_repositories
```

---

## 11. Querying

```
Call search_repository_code:
  query: "how is authentication handled"
  repo_name: "my-repo"    ← optional, omit to search all repos
  match_count: 10

Call perform_rag_query:
  query: "how to configure embeddings"
  source: "github.com"    ← optional filter

Call gather_task_context:
  task: "implement OAuth login"

Call resolve_include_chain:
  repo_name: "chip-a-drivers"
  file_path: "src/clk.c"
  max_depth: 5
  # Returns the full transitive #include tree across all indexed repos
```

---

## 12. Removing / Re-indexing a Repo Manually

If you need to delete a repo from the database directly:

```bash
docker exec -it supabase-db psql -U postgres -d postgres
```

```sql
-- Find source_id
SELECT source_id, summary FROM sources;

-- Delete all data for a repo
DELETE FROM crawled_pages WHERE source_id = 'repo:my-repo';
DELETE FROM code_examples WHERE source_id = 'repo:my-repo';
DELETE FROM sources WHERE source_id = 'repo:my-repo';

\q
```

---

## 13. Maintenance

### Restart the MCP server after code changes

```bash
# On server
cd /home/bapvesm013t/khushal/RAG_MCP
docker stop altera-rag && docker rm altera-rag
docker build -t altera-rag --build-arg PORT=8051 .
docker run -d \
  --name altera-rag \
  --env-file .env \
  --network host \
  --restart unless-stopped \
  -v /home/bapvesm013t/.netrc:/root/.netrc:ro \
  altera-rag
```

### Check container status

```bash
docker ps | grep altera-rag
docker logs --tail 50 altera-rag
```

### Restart Ollama

```bash
# Stop cleanly
sudo systemctl stop ollama 2>/dev/null || sudo lsof -ti:11434 | xargs sudo kill -9
sleep 2

# Restart with load settings
OLLAMA_NUM_PARALLEL=36 \
OLLAMA_NUM_THREAD=80 \
OLLAMA_MAX_LOADED_MODELS=2 \
ollama serve &

# Verify
ss -tlnp | grep 11434
```

---

## 14. Feature Flags Reference

| Flag | Default | What it does |
|---|---|---|
| `USE_CONTEXTUAL_EMBEDDINGS` | false | Adds LLM-generated context to each chunk before embedding. Slower but more accurate. Requires `MODEL_CHOICE` (llama3.2). |
| `USE_HYBRID_SEARCH` | false | Combines vector search + keyword (BM25) search. |
| `USE_AGENTIC_RAG` | false | Extracts code examples into a separate table for code-specific queries. |
| `USE_RERANKING` | false | Re-ranks results using a cross-encoder model after retrieval. |
| `USE_KNOWLEDGE_GRAPH` | false | Builds a Neo4j structural graph (File/Class/Method nodes). Requires a running Neo4j instance. |
| `USE_IMAGE_OCR` | false | Tesseract OCR for images and embedded images in PDF/DOCX. Requires rebuild (tesseract-ocr in Dockerfile). |
| `USE_IMAGE_VISION` | false | llava vision LLM for diagrams and images. Requires `ollama pull llava`. No rebuild needed. |
| `VISION_MODEL` | llava | Ollama vision model name. |
| `IMAGE_OCR_MIN_CHARS` | 50 | If OCR finds fewer chars than this, also run vision LLM as fallback. |

> All false is the recommended starting point — basic RAG works well without any of them.

---

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| `git: not found` in container | Rebuild image — git is now in Dockerfile |
| `Supabase Invalid URL` | Check `SUPABASE_URL=http://localhost:8000` in `.env` |
| `foreign key constraint` error | `source_id` mismatch — fixed in current `utils.py` |
| Embedding context length exceeded | Increase `EMBEDDING_MAX_CHARS` (default 1800) or reduce `CHUNK_SIZE` |
| Cursor can't connect | Check SSH tunnel is active; verify endpoint is `/mcp` not `/sse` |
| `description` kwarg error on FastMCP | Already removed in current `altera_rag.py` |
| Container exits immediately | Run `docker logs altera-rag` to see error |
| Ollama port already in use | `sudo systemctl stop ollama` or `sudo lsof -ti:11434 \| xargs sudo kill -9` |
| llava not found | `ollama pull llava` on the server |
| OCR returns empty text | Install `tesseract-ocr` in Dockerfile (requires rebuild); verify with `docker exec altera-rag tesseract --version` |
| Image indexing slow | Set `USE_IMAGE_VISION=false` to use OCR only, or process images in smaller batches |
