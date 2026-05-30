FROM node:20-slim

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pre-install the Bright Data MCP package so first run is fast
RUN npx --yes @brightdata/mcp --version 2>/dev/null || true

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["python3", "-m", "streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
