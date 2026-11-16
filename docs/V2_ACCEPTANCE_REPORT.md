# TANK650 ENGINE 2.0 — Acceptance Report

Status in this document is completed only after the final commands listed below pass.

| Criterion | Implementation/evidence |
|---|---|
| Existing golden values invariant | Engine formulas unchanged; full `pytest` suite executed at release. |
| Design Assistant tests | `backend/tests/integration/test_design_assistant.py` covers provenance, true PASS, locked conditions and immutability. |
| No orphan percentages | Inspector and workspace render title + demand/capacity + unit for every check; UI test asserts identity. |
| No meaningless empty tabs | Capability registry removes Results/Checks from configuration and representative geometry modules. |
| Active run across workspaces | Run/result state is global to `useTankWorkspace`; navigation only changes module/mode. |
| Failure explanation | Design Resolution displays demand, capacity, difference, utilization, reference and classification. |
| Real variant simulation | Each candidate calls the Python calculation engine and persists a `CalculationRun`. |
| Reproducible recommendations | Stored search space, values tested, changes, engine version, profile, score and run IDs. |
| Partial adoption | Apply endpoint filters the draft changeset and requires recalculation. |
| Revision immutable | Apply endpoint returns draft data only; integration test re-reads unchanged revision inputs. |
| Palette | Central V2 tokens and Three.js selection use the supplied blue/grey/white system. |
| Production build | `pnpm build` executed at release. |
| API documentation | `docs/API.md` and OpenAPI routes updated. |

## Release verification commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
pnpm test -- --run
pnpm build
```

## Final evidence

- Backend: **13 tests passed**.
- Frontend: **2 tests passed** in the V2 application suite.
- Production bundle: completed successfully with Vite; the existing bundle-size advisory is non-blocking.
- Runtime smoke test: `/api/v1/health` returned `engine_version: 2.0.0` and the browser loaded the V2 interface from `http://127.0.0.1:8000/`.
- Visual audit: capability-driven tabs, active-run header and V2 palette were inspected in the running build.
