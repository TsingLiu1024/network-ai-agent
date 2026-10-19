# Execution ledger — plan: 2026-10-19-hardening.md

Baseline a99af5e: clean checkout, pytest collected zero tests. Worktree branch
fix/diagnosis-hardening in outputs/network-ai-agent.

Authorization: user explicitly requested implementing all preceding review findings;
proceed with concrete repairs without repeated approval of the same scope.
Dependencies: Settings and LLMError underpin agents and API; ToolResult and
source-bearing retrieval underpin orchestration; orchestration status underpins
API responses. No contradictory shared interfaces found in preflight.


Task 1 complete: 12 provider/config regressions RED -> GREEN.
Task 2 complete: 15 tool/evidence/repair regressions RED -> GREEN (suite 27).
Task 3 complete: 8 initial retrieval regressions RED -> GREEN (suite 35).
Task 4 complete: 15 initial manager/API regressions RED -> GREEN (suite 50).
Task 5 complete: deployment/docs/CI, guarded scripts and further regressions.
Clean virtualenv install and pip check passed; actual uvicorn demo-process smoke
passed. Compose config validated using a copied .env.example. Docker build cannot
run because the Docker Desktop Linux engine pipe is absent.

Design decision: store validated JSON vectors and rebuild FAISS in memory, rather
than deserialize a disk FAISS binary; this removes both pickle and native binary
index parsing from the trust boundary, with a small startup cost.

Independent final review: hardening_review found two actionable issues.
Final: fixed parent capacity released before evidence workers finish —
test_manager_does_not_finish_while_evidence_workers_still_run RED -> GREEN.
Final: fixed overflowing vector scalars blocking snapshot recovery —
test_invalid_vector_scalar_recovers_from_snapshot RED -> GREEN.
Malformed JSON, prompt redaction, streamed response byte limits, late summary
budgets and HTTP timeout capacity now have regression coverage.
Suite currently 74/74, original environment; fresh environment final run pending.
No deferred minor findings. No push, deployment or real host repair performed.

Final verification: 76/76 tests passed in the fully locked clean environment;
Ruff, compileall, pip check and Compose config passed. Actual multilingual model
retrieval and offline cache reuse through the API passed. Four-sample Hit@3=1.0,
MRR=0.833. Both full/dev hashed lock installations passed. PyPI release-specific
known-vulnerability queries returned no active findings for 62 locked versions.
Shutdown and credential echo regressions RED -> GREEN. Task 6 complete.
Docker runtime unavailable; no remote CI, paid model call, upstream push or real
host repair. See docs/VALIDATION.md for exact limits and evidence.

Final additional regression: legacy environment aliases override dotenv defaults. Final suite 77/77. Dependency lock and reports included.
