# UI Audit V2

## Corrections

- Universal tabs were replaced by `moduleCapabilities`. Project, Code, Geometry, Product, Materials and Roof now expose only their meaningful configuration/model view.
- The false “No calculation run selected” geometry state was caused by looking for `result.modules.geometry`, which does not exist. The meaningless Result tab was removed instead of hiding the defect.
- Check views now consume the actual backend keys: `title`, `standard_reference`, `description`, `demand`, `capacity`, `unit`, `utilization` and `status`.
- Every utilization percentage is rendered with a visible check title and demand/capacity context; raw precision is available in the title tooltip.
- Failed checks open Design Resolution with failure magnitude, classification, editable/fixed variables and simulated alternatives.
- Navigation does not clear the active run. The header shows Project, Scenario, Revision, Run and Profile. Editing inputs marks existing results stale.
- Primary UI terminology is Spanish: Entradas, Resultados, Verificaciones, Propiedades and Cálculo.

The audited module matrix is in `UI_MODULE_AUDIT_V2.md` and `V2_IMPLEMENTATION_PLAN.md`.
