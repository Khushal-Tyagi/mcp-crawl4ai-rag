FROM python:3.12-slim

ARG PORT=8051

WORKDIR /app

# Install system dependencies including git and ssh client (for remote file indexing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    sshpass \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy only dependency files first (cached unless pyproject.toml changes)
COPY pyproject.toml .
COPY README.md .

# Install dependencies (cached layer - only re-runs if pyproject.toml changes)
RUN uv pip install --system -e . && \
    crawl4ai-setup

# Copy source code last (only this layer re-runs on code changes)
COPY . .

EXPOSE ${PORT}

# Command to run the MCP server
CMD ["python", "src/altera_rag.py"]
