# Design Assistant V2

The Design Assistant is deterministic, numerical and simulation-based. It does not change limits, environmental/project conditions, derived values or an engineer's active revision to manufacture a PASS.

## Cycle

`failed check → dependencies → eligible variables → candidate values → real calculation runs → ranking → draft changeset → engineer decision → recalculation`

`AUTO_ANCHORAGE` is classified as `ALTERNATIVE_PATH_FAIL` when mechanical anchorage passes; the overall design remains `PASS_WITH_MECHANICAL_ANCHORAGE`. For the T-78 study, annular nominal thickness is the eligible design choice and corrosion allowance is used to update its effective thickness deterministically. `Sp`, tank diameter and the API limit remain visible but locked.

Every study stores the source run, baseline revision, target check, variables, search space, engine/profile, candidate values, candidate run IDs, rankings and results. Applying all or part of a recommendation returns draft changes and `requires_recalculation: true`; it never creates or mutates a revision.

V2 limits a study to three variables and 500 simulations. Commercial/discrete values are evaluated as discrete candidates. The response records current value, a boundary estimate, first passing value and engineering-selected nominal value. A passing recommendation exists only when the target check passes in its associated calculation run.

The assistant does not use an LLM to determine compliance. A conversational model may explain persisted outputs but cannot assign engineering status.
