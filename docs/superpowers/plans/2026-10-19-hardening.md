# Diagnosis hardening implementation plan

> Execute inline with superpowers:executing-plans and TDD. One independent final review.

**Goal:** repair the reviewed reliability, evidence, execution, RAG and deployment defects.
**Spec:** ../specs/2026-10-19-hardening-design.md
**Architecture:** retain agent boundaries; bounded synchronous orchestration behind
an asynchronous API, centralized configuration, safe retrieval storage.
**Stack:** Python 3.12+, FastAPI, Pydantic, requests, FAISS, sentence-transformers.

## Global constraints
- No actual repair commands, paid models or upstream push during verification.
- No pickle index loading, generic shell execution or credentials in API errors.
- Local-host evidence explicitly labeled and cloud upload opt-in.
- API import must not download models or build indices.

## Review focus
- Concurrent request cancellation must not release capacity before workers finish.
- Missing/malformed LLM content must propagate as failed, not evidence.
- Empty/corrupt volumes and changed knowledge must recover without unsafe loading.
- DNS and subprocess timeouts must bound actual work, including Linux behavior.
- Repeated evidence in prompts must fit a bounded total input budget.

## Tasks (RED -> GREEN for each)
1. [x] Configuration and providers: tests/test_llm.py; config/settings.py,
   config/startup.py, llm/{base,factory,ollama,deepseek,openai,demo,validator}.py.
   Settings controls every endpoint/model/path. chat(prompt, timeout=None) returns
   str or LLMError. Tests assert actual transmitted payload and safe failures.
2. [x] Evidence and repair boundary: tests/test_tools.py, tests/test_agent.py;
   tools/*, agents/{network,log,repair}_agent.py, agents/core/result.py.
   Tools return ToolResult with return-code/timeouts respected. RepairPlan is
   validated and free-form execution fails closed; host evidence has scope.
3. [x] RAG persistence and evaluation: tests/test_rag.py; rag/*, knowledge/*,
   scripts/evaluate_rag.py. search returns source/score/chunk text, complete
   generations validated under lock; test with deterministic embeddings.
4. [x] Orchestration and API: tests/test_api.py, tests/test_manager.py;
   agents/core/manager.py, supervisor_agent.py, rag_agent.py; api/*, app.py.
   run(query) returns status/stages; sync work outside event loop with bounded
   admission, request IDs, auth, cancellation safety and readiness endpoint.
5. [x] Deployment and docs: README.md, docs/*, requirements*.txt, pyproject.toml,
   Dockerfile, docker-compose.yml, .dockerignore, .env.example, .github/workflows/*.
   Run offline full suite + Ruff + compileall + Compose validation. Attempt Docker
   build only if engine available. Record external verification limitations.
6. [x] Independent whole-change review and regression fixes; package code/patch
   and verification report for delivery. No push or live system repair.
