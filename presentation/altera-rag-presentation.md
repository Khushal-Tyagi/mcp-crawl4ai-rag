---
marp: true
theme: default
paginate: true
backgroundColor: #0a0e1a
color: #e2e8f0
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  :root {
    --blue:    #4f9cf9;
    --green:   #43d982;
    --orange:  #ff8c42;
    --purple:  #a78bfa;
    --cyan:    #22d3ee;
    --pink:    #f472b6;
    --yellow:  #fbbf24;
    --bg:      #0a0e1a;
    --bg2:     #111827;
    --bg3:     #1e2536;
    --border:  #2d3748;
  }

  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: var(--bg);
    color: #e2e8f0;
    padding: 40px 50px;
    font-size: 16px;
  }

  /* ── Headings ── */
  h1 {
    font-size: 1.95em;
    font-weight: 800;
    background: linear-gradient(90deg, var(--blue), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 18px;
    letter-spacing: -0.5px;
  }
  h2 {
    font-size: 1.35em;
    font-weight: 700;
    color: var(--cyan);
    margin-bottom: 12px;
  }
  h3 {
    font-size: 1.1em;
    font-weight: 600;
    color: var(--green);
  }

  /* ── Code ── */
  code {
    font-family: 'JetBrains Mono', monospace;
    background: #1a2035;
    color: var(--orange);
    border: 1px solid #2d3748;
    border-radius: 5px;
    padding: 1px 7px;
    font-size: 0.82em;
  }
  pre {
    font-family: 'JetBrains Mono', monospace;
    background: #0d1424;
    border: 1px solid #2a3550;
    border-left: 4px solid var(--blue);
    border-radius: 10px;
    padding: 18px 22px;
    font-size: 0.78em;
    line-height: 1.6;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  }
  pre code {
    background: none;
    border: none;
    padding: 0;
    color: #a8c8ff;
    font-size: 1em;
  }

  /* ── Tables ── */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82em;
    border-radius: 8px;
    overflow: hidden;
  }
  th {
    background: linear-gradient(90deg, #1a2540, #1e2d4a);
    color: var(--blue);
    padding: 10px 14px;
    border: 1px solid #2d3f60;
    font-weight: 700;
    letter-spacing: 0.3px;
  }
  td {
    padding: 8px 14px;
    border: 1px solid #1e2a3a;
    color: #c5d5e8;
  }
  tr:nth-child(even) td { background: #0f1626; }
  tr:hover td { background: #162035; }

  /* ── Lists ── */
  ul { line-height: 1.9; padding-left: 20px; }
  li { margin: 3px 0; color: #c8d8ec; }
  li::marker { color: var(--blue); }

  /* ── Blockquote ── */
  blockquote {
    border-left: 4px solid var(--purple);
    background: linear-gradient(90deg, #1a1535, #0f1320);
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    color: #a0b0cc;
    font-style: italic;
    margin: 12px 0;
  }

  /* ── TITLE SLIDE ── */
  section.title {
    background: radial-gradient(ellipse at 30% 40%, #0d2050 0%, #050a14 60%),
                radial-gradient(ellipse at 80% 80%, #0a1a30 0%, transparent 60%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  section.title h1 {
    font-size: 3em;
    line-height: 1.1;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #60a5fa, #22d3ee, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  section.title h2 {
    font-size: 1.3em;
    color: #64748b;
    font-weight: 400;
    -webkit-text-fill-color: #94a3b8;
  }
  section.title p { color: #64748b; font-size: 0.95em; }

  /* ── SECTION DIVIDER ── */
  section.divider {
    background: linear-gradient(135deg, #0a1628 0%, #0f2040 50%, #0a1628 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  section.divider h1 {
    font-size: 2.8em;
    background: linear-gradient(90deg, var(--blue), var(--green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  section.divider p { font-size: 1.1em; color: #64748b; }

  /* ── CARD GRID ── */
  .cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 14px;
  }
  .card {
    background: linear-gradient(135deg, #111827, #1a2235);
    border: 1px solid #2d3f60;
    border-radius: 12px;
    padding: 16px;
    font-size: 0.82em;
    line-height: 1.6;
  }
  .card-title {
    font-weight: 700;
    font-size: 0.95em;
    margin-bottom: 6px;
  }

  /* ── BADGE/PILL ── */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72em;
    font-weight: 600;
    margin: 2px;
  }
  .badge-blue  { background: #1a3a6a; color: #60a5fa; border: 1px solid #2a5090; }
  .badge-green { background: #0d3322; color: #34d399; border: 1px solid #1a5a3a; }
  .badge-orange{ background: #3a1d0a; color: #fb923c; border: 1px solid #6a3a15; }
  .badge-purple{ background: #2a1a50; color: #a78bfa; border: 1px solid #4a3080; }

  /* ── FLOW BOX ── */
  .flow-box {
    background: linear-gradient(135deg, #111827, #1a2438);
    border: 1px solid #2d4060;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: 0.83em;
  }
  .flow-arrow {
    text-align: center;
    color: var(--blue);
    font-size: 1.4em;
    line-height: 1.2;
    margin: 2px 0;
  }

  /* ── HIGHLIGHT BOX ── */
  .highlight {
    background: linear-gradient(90deg, #0d2040, #0a1a30);
    border: 1px solid #1e4080;
    border-left: 4px solid var(--blue);
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.88em;
    color: #93c5fd;
  }

  /* ── TWO-COL LAYOUT ── */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

  /* ── LAYER BOX ── */
  .layer {
    border-radius: 8px;
    padding: 10px 16px;
    margin: 4px 0;
    font-size: 0.82em;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .layer-num {
    font-size: 1.3em;
    font-weight: 800;
    min-width: 32px;
    text-align: center;
  }

  /* ── STAT CARDS ── */
  .stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-top: 16px; }
  .stat { background: #111827; border: 1px solid #2d3f60; border-radius: 12px; padding: 18px 12px; text-align: center; }
  .stat-num { font-size: 2em; font-weight: 800; background: linear-gradient(90deg,var(--blue),var(--cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .stat-label { font-size: 0.75em; color: #64748b; margin-top: 4px; }

  /* ── TOOL TAG ── */
  .tool { display: inline-block; background: #0f1e35; border: 1px solid #1e4070; border-radius: 6px; padding: 3px 9px; font-family: 'JetBrains Mono', monospace; font-size: 0.75em; color: #60a5fa; margin: 2px; }

  /* Paginator */
  section::after {
    font-size: 0.72em;
    color: #2d3f60;
  }

  strong { color: var(--orange); }
  em     { color: var(--cyan); }
---

<!-- _class: lead -->
<!-- _backgroundColor: #0d1117 -->

# 🧠 Altera RAG
## MCP Server — Private Codebase Intelligence

> **Semantic Search · Local Embeddings · Knowledge Graphs**

**Cursor + AI Assistants  →  Your Private Codebase**

---

# Agenda

1. 🎯 **What is this?** — Problem & Solution
2. 🏗️ **Architecture Overview** — System layers
3. 🔧 **Technologies Used** — Stack breakdown
4. 📡 **MCP Protocol** — How AI connects
5. 🔄 **Data Ingestion Flow** — How content gets indexed
6. 🔍 **RAG Pipeline** — How search works
7. 🧩 **Knowledge Graph** — Structural code analysis
8. 🛠️ **Tool Catalogue** — All 20+ tools
9. 🚀 **Deployment Flow** — Docker + SSH
10. 🔐 **Security Model** — Private-by-design

---

<!-- _class: center -->

# 🎯 The Problem

```
You're building embedded firmware for a custom FPGA chip.
Your codebase has 200,000 lines of C/C++, SystemRDL register maps,
PDF datasheets, and internal Git repos — all private.

Your AI assistant knows NOTHING about any of it.
```

### Every question ends with:

> *"I don't have access to your private codebase"*

---

# 💡 The Solution: Altera RAG MCP Server

```
┌─────────────────────────────────────────────────────────┐
│                   CURSOR (AI Assistant)                  │
│                         │                               │
│           asks → MCP Protocol ← responds               │
└─────────────────────────┼───────────────────────────────┘
                          │  HTTP / SSH Tunnel
                          ▼
┌─────────────────────────────────────────────────────────┐
│              ALTERA RAG MCP SERVER                       │
│   • Index private repos     • Crawl documentation       │
│   • Embed with Ollama        • Store in Supabase+pgvec  │
│   • Semantic search          • Knowledge graph (Neo4j)  │
└─────────────────────────────────────────────────────────┘
```

**Zero data leaves your network** — embeddings run via local **Ollama**

---

# 🏗️ Layered Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 5 │  CLIENT LAYER                                      │
│           │  Cursor IDE · AI Assistants · REST clients        │
├──────────────────────────────────────────────────────────────┤
│  LAYER 4 │  TRANSPORT LAYER                                   │
│           │  SSH Tunnel (port 8051) · HTTP/Streamable-HTTP    │
├──────────────────────────────────────────────────────────────┤
│  LAYER 3 │  MCP SERVER LAYER  (FastMCP / uvicorn)             │
│           │  Tool Router · Lifespan Manager · Context Pool    │
├──────────────────────────────────────────────────────────────┤
│  LAYER 2 │  INTELLIGENCE LAYER                                │
│           │  Crawl4AI · repo_context · RAG pipeline           │
│           │  Cross-encoder Reranking · Agentic RAG            │
├──────────────────────────────────────────────────────────────┤
│  LAYER 1 │  DATA LAYER                                        │
│           │  Supabase+pgvector · Neo4j · Ollama Embeddings    │
└──────────────────────────────────────────────────────────────┘
```

---

# 🔧 Technologies — Full Stack

| Layer | Technology | Role |
|-------|-----------|------|
| **Protocol** | Model Context Protocol (MCP) | AI ↔ Server contract |
| **Server** | FastMCP + uvicorn | Async HTTP server |
| **Web Crawling** | Crawl4AI | Browser-based crawler |
| **Embeddings** | Ollama `mxbai-embed-large` | 1024-dim local vectors |
| **Vision LLM** | Ollama `llava` | Block diagram understanding |
| **Vector DB** | Supabase + pgvector | Semantic similarity search |
| **Graph DB** | Neo4j | Code structure graph |
| **Reranking** | `sentence-transformers` CrossEncoder | Search quality boost |
| **PDF/DOCX** | pdfplumber, python-docx | Doc parsing |
| **OCR** | Tesseract | Text extraction from images |
| **Deployment** | Docker + SSH | Containerized on Linux server |

---

<!-- _class: center -->

# 📡 MCP Protocol — How It Works

```
Cursor / AI Client
       │
       │  1. Tool Discovery   GET /mcp  ───► MCP Server lists all tools
       │                                     with their schemas
       │
       │  2. Tool Invocation  POST /mcp ───► { "tool": "perform_rag_query",
       │                                        "args": { "query": "..." } }
       │
       │  3. Streaming Result ◄─────────     Server streams response back
       │
       ▼
 AI uses result as context for its next reply
```

**Transport:** `streamable-http` on port **8051**
**Auth:** SSH tunnel — no credentials exposed externally

---

# 🔄 Data Ingestion Flow — Web Crawl

```
   User asks: smart_crawl_url("https://docs.example.com")
        │
        ▼
   ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐
   │  URL Type   │    │   Crawl4AI       │    │  Text Chunks   │
   │  Detection  │──► │  Async Browser   │──► │  (1500 chars)  │
   │             │    │  Crawler         │    │                │
   └─────────────┘    └──────────────────┘    └───────┬────────┘
   sitemap → batch                                     │
   .txt → parallel                                     ▼
   webpage → recursive                    ┌────────────────────┐
                                          │  Ollama Embedding  │
                                          │  mxbai-embed-large │
                                          │  → 1024-dim vector │
                                          └──────────┬─────────┘
                                                     │
                                                     ▼
                                          ┌────────────────────┐
                                          │  Supabase+pgvector │
                                          │  crawled_pages     │
                                          └────────────────────┘
```

---

# 🔄 Data Ingestion Flow — Repository Indexing

```
   index_repository_source("https://github.com/org/repo.git")
        │
        ▼
   ┌──────────────┐   ┌────────────────┐   ┌───────────────────┐
   │  Git Clone   │   │  File Filter   │   │  File Processor   │
   │  (with auth) │──►│  by extension  │──►│  per type:        │
   │  to /tmp     │   │  .py .cpp .rdl │   │  • source → text  │
   └──────────────┘   │  .pdf .docx    │   │  • PDF → extract  │
                      │  .png .jpg     │   │  • Image → OCR    │
                      └────────────────┘   │  • DOCX → text    │
                                           └────────┬──────────┘
                                                    │
                                                    ▼
                                        ┌───────────────────────┐
                                        │   Chunk → Embed       │
                                        │   store in Supabase   │
                                        │   url = repo://name/  │
                                        └───────────────────────┘
```

---

# 🔍 RAG Pipeline — Search Flow

```
   perform_rag_query("How does the AXI bus interrupt work?")
        │
        ▼
   ┌──────────────────────────────────────────────────────┐
   │  STEP 1: Embed the query                              │
   │  query → Ollama mxbai-embed-large → [1024 floats]    │
   └──────────────────────────────┬───────────────────────┘
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────┐
   │  STEP 2: Vector Similarity Search                     │
   │  pgvector cosine similarity → top-K candidates       │
   │  (optional: + keyword FTS for hybrid search)         │
   └──────────────────────────────┬───────────────────────┘
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────┐
   │  STEP 3: Reranking (optional)                         │
   │  CrossEncoder(query, doc) → re-scored & sorted       │
   └──────────────────────────────┬───────────────────────┘
                                  │
                                  ▼
                        Top results returned to AI
```

---

# 🔍 RAG Strategies — Feature Matrix

| Strategy | Config Flag | Effect |
|----------|------------|--------|
| **Basic** | *(default)* | Single-stage vector similarity |
| **Contextual Embeddings** | `USE_CONTEXTUAL_EMBEDDINGS=true` | LLM enriches each chunk before embedding |
| **Hybrid Search** | `USE_HYBRID_SEARCH=true` | Vector + FTS keyword combined |
| **Agentic RAG** | `USE_AGENTIC_RAG=true` | Extracts & indexes code blocks separately |
| **Reranking** | `USE_RERANKING=true` | CrossEncoder re-scores top-K results |
| **Knowledge Graph** | `USE_KNOWLEDGE_GRAPH=true` | Symbol lookup via Neo4j |

> All strategies **stack** — you can enable any combination

---

# 🧩 Knowledge Graph Layer

```
   parse_github_repository("https://github.com/org/repo")
        │
        ▼
   ┌──────────────────────────────────────────────────────────┐
   │  Python AST Parser                                        │
   │  Extracts: Files, Classes, Methods, Functions, Imports   │
   └──────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────────┐
   │              NEO4J GRAPH                                  │
   │                                                           │
   │  (File)─[CONTAINS]─►(Class)─[HAS_METHOD]─►(Method)      │
   │      │                                                    │
   │      └─[IMPORTS]──►(ExternalModule)                       │
   └──────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
   Enables: find_symbol_across_repos("AXIBusMaster")
            resolve_include_chain("top.h")
            check_ai_script_hallucinations("gen_script.py")
```

---

# 🤖 AI Hallucination Detection

```
   check_ai_script_hallucinations("ai_generated_code.py")
        │
        ▼
   ┌─────────────────────┐    ┌───────────────────────────────┐
   │  AI Script Analyzer  │    │  Knowledge Graph Validator   │
   │                      │    │                               │
   │  • Parse imports     │──► │  • Does class exist?          │
   │  • Extract calls     │    │  • Does method exist?         │
   │  • Find symbols      │    │  • Is signature correct?      │
   └─────────────────────┘    └───────────────────────────────┘
                                            │
                                            ▼
                               ┌────────────────────────────┐
                               │  Hallucination Reporter    │
                               │                            │
                               │  ✅ Valid symbols          │
                               │  ❌ Hallucinated APIs      │
                               │  ⚠️  Deprecated usage      │
                               └────────────────────────────┘
```

---

# 🛠️ Tool Catalogue — Web & Search

| Tool | Description |
|------|-------------|
| `crawl_single_page` | Crawl one URL → store as searchable content |
| `smart_crawl_url` | Auto-detect: sitemap / txt / webpage → recursive crawl |
| `get_available_sources` | List all indexed domains/sources |
| `perform_rag_query` | Semantic search over crawled docs |
| `search_code_examples` | Search extracted code blocks *(agentic mode)* |

---

# 🛠️ Tool Catalogue — Repository & Files

| Tool | Description |
|------|-------------|
| `index_repository_source` | Clone + index a Git repo (private or public) |
| `update_repository` | Re-index a repo by stored name |
| `list_indexed_repositories` | List all repos in Supabase + Neo4j |
| `index_local_path` | Index files from server filesystem |
| `index_remote_path` | SCP files from another machine + index |
| `prepare_cursor_machine_upload` | Get SCP command for laptop → server upload |
| `search_repository_code` | Semantic search over indexed source files |
| `get_repository_file` | Fetch a specific file by repo + path |
| `gather_task_context` | Unified context: snippets + symbols for a task |
| `find_symbol_across_repos` | Find class/function/method by name |
| `resolve_include_chain` | Trace `#include` dependencies across repos |

---

# 🛠️ Tool Catalogue — Knowledge Graph

| Tool | Description |
|------|-------------|
| `parse_github_repository` | Parse repo into Neo4j nodes + relationships |
| `check_ai_script_hallucinations` | Validate AI-generated code vs. knowledge graph |
| `query_knowledge_graph` | Run raw Cypher queries on Neo4j |

---

# 🚀 Deployment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  WINDOWS LAPTOP (Cursor IDE)                                  │
│  mcp.json:                                                    │
│  { "url": "http://localhost:8051/mcp", "timeout": 7200 }     │
└───────────────────────────┬──────────────────────────────────┘
                            │  SSH Tunnel
                            │  ssh -L 8051:localhost:8051
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  LINUX SERVER                                                 │
│  ┌─────────────────────┐  ┌────────────────┐  ┌──────────┐  │
│  │  altera-rag          │  │  Supabase       │  │  Ollama  │  │
│  │  Docker Container    │  │  Docker Stack   │  │  daemon  │  │
│  │  port 8051           │  │  PostgreSQL     │  │  :11434  │  │
│  │                     │  │  + pgvector     │  │          │  │
│  └─────────────────────┘  └────────────────┘  └──────────┘  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Neo4j  (optional)   port 7474 / 7687                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

# 🚀 Deployment Steps

```
1. Clone repo on Linux server
   git clone <repo-url>

2. Apply SQL schema to Supabase
   psql -f crawled_pages.sql

3. Configure .env
   EMBEDDING_BASE_URL=http://localhost:11434/v1
   SUPABASE_URL=http://localhost:8000
   USE_KNOWLEDGE_GRAPH=false   # enable when Neo4j ready

4. Build Docker image
   docker build -t altera-rag --build-arg PORT=8051 .

5. Run container
   docker run -d --name altera-rag --network host \
     --env-file .env altera-rag

6. Open SSH tunnel from Windows
   ssh -L 8051:localhost:8051 user@SERVER_IP
```

---

# 🖼️ Image & Document Processing

```
  Input File
      │
      ├─── .pdf  ──►  pdfplumber extract text
      │                    + embedded images ──►  ┐
      │                                            │
      ├─── .docx ──►  python-docx extract text    │
      │                    + embedded images ──►  ┤
      │                                            │
      ├─── .png/.jpg ──────────────────────────►  ┤
      │                                            ▼
      │                              ┌─────────────────────┐
      │                              │  OCR (Tesseract)     │
      │                              │  good for: tables,   │
      │                              │  screenshots, text   │
      │                              └──────────┬──────────┘
      │                                         │ if < 50 chars
      │                                         ▼
      │                              ┌─────────────────────┐
      │                              │  Vision LLM (llava)  │
      │                              │  good for: diagrams  │
      │                              │  block diagrams      │
      └──────────────────────────────└─────────────────────┘
```

---

# 🔐 Security Model

```
┌─────────────────────────────────────────────────────────────┐
│  PRIVATE BY DESIGN                                           │
│                                                             │
│  ✅ Embeddings run locally (Ollama) — no cloud calls        │
│  ✅ Database self-hosted (Supabase Docker)                   │
│  ✅ Server accessible only via SSH tunnel                    │
│  ✅ No API keys required for embeddings                      │
│  ✅ Git auth via .netrc / SSH keys (not env vars)           │
│  ✅ Remote credentials stored in remote_systems.json        │
│     (not hardcoded, file-permission controlled)             │
│                                                             │
│  Auth boundary:                                             │
│  Cursor → SSH → Linux server → localhost:8051               │
│  No port 8051 exposed externally                            │
└─────────────────────────────────────────────────────────────┘
```

---

# 📊 Embedding & Chunking Strategy

```
Document / Source File
        │
        ▼
   ┌──────────────────────────────────────┐
   │  Chunk Size: 1500 chars (default)    │
   │  Overlap: paragraph-aware splitting  │
   └──────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────┐
   │  Contextual Embedding (optional)     │
   │  LLM prepends document context to   │
   │  each chunk before embedding         │
   │  → better semantic representation   │
   └──────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────┐
   │  mxbai-embed-large                   │
   │  1024 dimensions                     │
   │  Max 1800 chars per embedding call   │
   │  Parallel batch processing           │
   │  (EMBEDDING_PARALLEL_BATCHES=32)     │
   └──────────────────────────────────────┘
```

---

# 🔄 Cross-Repository Symbol Lookup

```
   find_symbol_across_repos("InterruptController")
        │
        ▼
   ┌─────────────────────────────────────────────────────┐
   │  Two-pronged search:                                  │
   │                                                       │
   │  1. Supabase semantic search                          │
   │     → finds code chunks mentioning the symbol        │
   │                                                       │
   │  2. Neo4j graph lookup (if enabled)                   │
   │     MATCH (c:Class {name: "InterruptController"})    │
   │     RETURN c, c.file, c.methods                      │
   └────────────────────┬────────────────────────────────┘
                        │
                        ▼
             Combined result: which repos,
             which files, what signatures
```

---

# ⚙️ `gather_task_context` — Unified Intelligence

```
   gather_task_context("implement DMA burst transfer for AXI4")
        │
        ├──► search_repository_code("DMA burst transfer AXI4")
        │         │
        │         └── Returns: top 5 code snippets across all repos
        │
        ├──► find_symbol_across_repos("DMA", "AXI4", "burst")
        │         │
        │         └── Returns: matching class/function definitions
        │
        └──► Repo metadata + source file paths
                  │
                  ▼
        ┌─────────────────────────────────────────┐
        │  Unified JSON context bundle:            │
        │  { snippets: [...], symbols: [...],      │
        │    repos: [...], task_summary: "..." }   │
        └─────────────────────────────────────────┘
              Injected into AI assistant's context
```

---

# 📁 Supported File Types

| Category | Extensions |
|----------|------------|
| **Python** | `.py` |
| **C / C++** | `.c` `.cpp` `.h` `.hpp` `.cc` `.cxx` |
| **Hardware / Register** | `.rdl` `.ralf` `.ipxact` |
| **Web / Script** | `.js` `.ts` `.jsx` `.tsx` `.html` `.css` `.sh` |
| **Data / Config** | `.csv` `.tsv` `.xml` `.json` `.yaml` `.toml` |
| **Documentation** | `.md` `.rst` `.pdf` `.docx` |
| **Images** | `.png` `.jpg` `.jpeg` `.tiff` `.bmp` `.gif` `.webp` |
| **Database** | `.sql` |
| **Other Languages** | `.java` `.rs` `.go` `.rb` `.kt` `.swift` `.scala` |
| **HDL** | `.sv` `.v` `.vhd` |

---

# 🔄 Incremental Indexing & Updates

```
  Already indexed repo "chiplib" at commit abc123
        │
        ▼
  update_repository("chiplib")    OR    index_repository_source(url, skip_existing=True)
        │                                         │
        ▼                                         ▼
  ┌─────────────────────┐           ┌─────────────────────────┐
  │  Re-clone from URL  │           │  Skip files already in  │
  │  stored in Supabase │           │  Supabase by URL hash   │
  │  sources table      │           │  → only index new files │
  └─────────────────────┘           └─────────────────────────┘
        │
        ▼
  Full re-index with fresh embeddings
  (existing records overwritten by URL)
```

---

# 🌐 Remote File Indexing — SCP Flow

```
   index_remote_path(remote_path="/projects/fpga", host="192.168.1.50",
                     user="eng", password="...", system_name="fpga-server")
        │
        ▼
   ┌───────────────────────────────────────────────────────┐
   │  1. Save credentials to remote_systems.json           │
   │     (only if save_credentials=True)                   │
   └──────────────────────────────┬────────────────────────┘
                                  │
                                  ▼
   ┌───────────────────────────────────────────────────────┐
   │  2. SCP copy to staging dir on server                 │
   │     /tmp/altera-rag-remote-<hash>/                    │
   └──────────────────────────────┬────────────────────────┘
                                  │
                                  ▼
   ┌───────────────────────────────────────────────────────┐
   │  3. index_local_directory(staging_dir)                │
   │     → standard chunking + embedding pipeline          │
   └───────────────────────────────────────────────────────┘
```

---

# 🏁 Summary — What Makes It Special

| Feature | Why It Matters |
|---------|----------------|
| **100% Local Embeddings** | Private data never leaves the network |
| **Any file type** | PDFs, images, hardware files, source code |
| **Cross-repo symbol search** | Find APIs across 50+ repos instantly |
| **Knowledge graph** | Detect AI hallucinations in generated code |
| **Incremental indexing** | Only re-index what changed |
| **SSH-secured access** | No external ports exposed |
| **Docker deployment** | One-command deploy, volume-mounted for hot reload |
| **MCP protocol** | Works with Cursor, Claude, any MCP-compatible client |

---

<!-- _class: lead -->

# Thank You

## Altera RAG MCP Server

**Private Codebase Intelligence for AI Assistants**

```
Cursor IDE  →  SSH Tunnel  →  MCP Server
              →  Ollama  →  Supabase+pgvector
              →  Neo4j Knowledge Graph
```

> *All data stays private. All embeddings stay local.*

**Questions?**
