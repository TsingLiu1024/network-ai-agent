FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HF_HOME=/app/model_cache
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends iputils-ping dnsutils libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 agent && useradd --uid 10001 --gid agent --create-home agent
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY --chown=agent:agent . .
RUN mkdir -p /app/vector_db /app/model_cache && chown -R agent:agent /app/vector_db /app/model_cache
USER agent
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
