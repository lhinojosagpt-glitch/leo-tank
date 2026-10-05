# OpenSCAD

`backend/app/openscad/generator.py` genera un `.scad` paramétrico desde `TankGeometrySpec`.

- Los ocho cursos se generan mediante llamadas parametrizadas.
- Los 60 pernos se generan con un `for`, no manualmente.
- OpenSCAD no es requisito para crear el archivo.
- Si `OPENSCAD_PATH` está configurado, una futura tarea puede invocar CLI para STL/3MF/PNG.

El export actual se obtiene con `POST /api/v1/runs/{run_id}/export/scad`.

