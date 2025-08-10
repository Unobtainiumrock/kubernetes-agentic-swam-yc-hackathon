FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install API requirements
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

# Copy google-adk source and install its requirements
COPY google-adk/requirements.txt ./google-adk-requirements.txt
RUN pip install --no-cache-dir -r google-adk-requirements.txt

# Copy google-adk source code
COPY google-adk/src /deps

# Copy API code and agents
COPY api/app ./app
COPY api/agents ./agents
COPY api/autonomous_monitor.py ./
COPY api/log_streamer.py ./

# Create reports directory
RUN mkdir -p /root/reports

ENV PYTHONPATH=/app:/deps
ENV ADK_CONFIG_PATH=/deps/adk_agent/config/runtime.yaml
ENV BACKEND_URL=http://localhost:8001

EXPOSE 8888
CMD ["python", "autonomous_monitor.py"]
