# Database

SQLite es la base local. SQLAlchemy 2 modela:

- `projects`
- `design_scenarios`
- `scenario_revisions`
- `calculation_runs`
- `variant_batches`
- `artifacts`
- `audit_events`

Una `ScenarioRevision` contiene un snapshot JSON y un delta legible. Al crear un run se marca `locked=true`. Los cambios posteriores deben crear una nueva revisión con `derived_from_revision_id`.

Los resultados de un run incluyen el hash SHA-256 de inputs, versión del motor, perfil normativo, trazas, verificaciones y snapshot geométrico.

La migración inicial está en `backend/alembic/versions/0001_initial.py`.

