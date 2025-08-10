FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

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

ENV PYTHONPATH=/app:/deps
ENV ADK_CONFIG_PATH=/deps/adk_agent/config/runtime.yaml
EXPOSE 8888
CMD ["python", "-m", "app.server"]
