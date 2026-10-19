# Contributing

Use Python 3.12/3.13 and an isolated virtual environment. Install
`requirements-dev.lock` with `pip install --require-hashes -r requirements-dev.lock`, then run `python -m pytest -q`,
`python -m ruff check .` and `python -m ruff format --check .`.

Tests are offline: replace external HTTP/subprocess operations with fixtures,
not the component under test. Never execute actual repair commands or use real
credentials in tests. Retrieval tests use deterministic embeddings and real FAISS.
Real-model retrieval evaluation is a separate explicit command.

Add a regression that fails first for each behavioral repair. Cover successful,
failed and partial results, timeouts, privacy controls and concurrency where relevant.
Use fix/, feature/ or docs/ branches; explain behavior and validation in PRs.
Do not commit .env, logs, model caches or vector volumes.
