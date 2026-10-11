from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


MEMORY_FORMAT_VERSION = "1.0"
NAVY = "17384A"
DEEP_BLUE = "0B4E66"
PALE_BLUE = "EEF5F8"
LIGHT_GRAY = "D9E1E5"
MID_GRAY = "627985"
BLACK = "000000"
WHITE = "FFFFFF"
FIXED_ZIP_TIME = (2000, 1, 1, 0, 0, 0)


def _set_run_font(run, size: float = 9.5, bold: bool = False, color: str = BLACK, name: str = "Aptos") -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def _shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def _cell_margins(cell, top: int = 100, start: int = 110, bottom: int = 100, end: int = 110) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def _set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "5")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), LIGHT_GRAY)
        borders.append(node)


def _repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def _prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def _format_number(value: Any, digits: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    if isinstance(value, float):
        magnitude = abs(value)
        if magnitude >= 1_000_000:
            return f"{value:,.0f}".replace(",", " ")
        if magnitude >= 1_000:
            return f"{value:,.2f}".replace(",", " ")
        return f"{value:.{digits}f}"
    return str(value)


def _format_inputs(values: dict[str, Any]) -> str:
    parts = []
    for key in sorted(values):
        value = values[key]
        if isinstance(value, dict):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        else:
            rendered = _format_number(value, 6)
        parts.append(f"{key} = {rendered}")
    return "; ".join(parts)


def _add_body(doc: Document, text: str, after: float = 5.0) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.08
    paragraph.paragraph_format.widow_control = True
    run = paragraph.add_run(text)
    _set_run_font(run, size=9.5)


def _add_heading(doc: Document, text: str, level: int = 1, page_break_before: bool = False) -> None:
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.page_break_before = page_break_before
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_before = Pt(10 if level == 1 else 7)
    paragraph.paragraph_format.space_after = Pt(5)
    size = 16 if level == 1 else 12 if level == 2 else 10.5
    for run in paragraph.runs:
        _set_run_font(run, size=size, bold=True, color=BLACK, name="Aptos Display")


def _add_table(
    doc: Document,
    headers: list[str],
    rows: Iterable[Iterable[Any]],
    widths_cm: list[float] | None = None,
    numeric_columns: set[int] | None = None,
    keep_together: bool = False,
    add_spacer: bool = True,
):
    numeric_columns = numeric_columns or set()
    row_values = list(rows)
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_borders(table)
    header_row = table.rows[0]
    _repeat_header(header_row)
    _prevent_row_split(header_row)
    for index, header in enumerate(headers):
        cell = header_row.cells[index]
        if widths_cm:
            cell.width = Cm(widths_cm[index])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        _cell_margins(cell, top=105, bottom=105)
        _shade(cell, DEEP_BLUE)
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(0)
        if keep_together:
            paragraph.paragraph_format.keep_with_next = True
        run = paragraph.add_run(header)
        _set_run_font(run, size=8.4, bold=True, color=WHITE)
    for row_index, values in enumerate(row_values):
        row = table.add_row()
        _prevent_row_split(row)
        for col_index, value in enumerate(values):
            cell = row.cells[col_index]
            if widths_cm:
                cell.width = Cm(widths_cm[col_index])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            _cell_margins(cell)
            if row_index % 2 == 1:
                _shade(cell, PALE_BLUE)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT if col_index in numeric_columns else WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            if keep_together and row_index < len(row_values) - 1:
                paragraph.paragraph_format.keep_with_next = True
            run = paragraph.add_run(str(value))
            _set_run_font(run, size=8.1)
    if add_spacer:
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(2)
    return table


def _add_key_value_table(doc: Document, rows: list[tuple[str, Any, str]], widths_cm: list[float] | None = None) -> None:
    values = [(label, _format_number(value), unit) for label, value, unit in rows]
    _add_table(doc, ["Parámetro", "Valor", "Unidad"], values, widths_cm or [10.2, 4.0, 3.0], {1})


def _add_status_summary(doc: Document, result: dict[str, Any]) -> None:
    summary = result["summary"]
    rows = [
        ("Casco", summary["shell"]["status"], f"Utilización máxima por presión {summary['shell']['max_utilization']:.1%}"),
        ("Fondo", summary["bottom"]["status"], "Placas central y anular verificadas"),
        ("Viento", summary["wind"]["status"], "Anclajes requeridos: " + ("Sí" if summary["wind"]["anchors_required"] else "No")),
        ("Sismo", summary["seismic"]["status"], f"J = {summary['seismic']['J']:.4f}"),
        ("Autoanclaje", summary["auto_anchor"]["status"], summary["auto_anchor"]["classification"].replace("_", " ")),
        ("Anclaje mecánico", summary["anchorage"]["status"], f"{summary['anchorage']['selected_bolts']} pernos seleccionados"),
    ]
    _add_table(doc, ["Módulo", "Estado", "Indicador"], rows, [4.1, 3.4, 9.7])


def _add_checks(doc: Document, module_name: str, module: dict[str, Any]) -> None:
    checks = module.get("checks", [])
    if not checks:
        return
    _add_heading(doc, f"Verificaciones de {module_name}", 2)
    rows = []
    for check in checks:
        utilization = "-" if check.get("utilization") is None else f"{check['utilization']:.2%}"
        rows.append(
            (
                check["title"],
                _format_number(check.get("demand")),
                _format_number(check.get("capacity")),
                check.get("unit", ""),
                utilization,
                check["status"],
                check.get("standard_reference", ""),
            )
        )
    _add_table(
        doc,
        ["Verificación", "Demanda", "Capacidad", "Unidad", "Utilización", "Estado", "Referencia"],
        rows,
        [4.7, 2.4, 2.4, 1.5, 1.9, 1.8, 2.8],
        {1, 2, 4},
    )


def _add_trace(doc: Document, trace: dict[str, Any]) -> None:
    _add_heading(doc, f"{trace['symbol']} {trace['description']}", 3)
    rows = [
        ("Identificador", trace["formula_id"]),
        ("Referencia", trace["reference"]),
        ("Ecuación", trace["expression"]),
        ("Variables de entrada", _format_inputs(trace.get("inputs", {}))),
        ("Resultado bruto", _format_number(trace.get("raw_result"), 8)),
        ("Resultado mostrado", f"{_format_number(trace.get('display_result'), 6)} {trace.get('unit', '')}".strip()),
        ("Redondeo", trace.get("rounding", "")),
        ("Estado", trace.get("status", "CALCULATED")),
    ]
    _add_table(doc, ["Campo", "Contenido"], rows, [4.0, 13.2], keep_together=True, add_spacer=False)


def _configure_document(doc: Document, result: dict[str, Any]) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.55)
    section.bottom_margin = Cm(1.55)
    section.left_margin = Cm(1.75)
    section.right_margin = Cm(1.75)
    section.header_distance = Cm(0.65)
    section.footer_distance = Cm(0.65)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor.from_string(BLACK)

    title = doc.styles["Title"]
    title.font.name = "Aptos Display"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
    title.font.size = Pt(27)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(BLACK)

    for style_name, size in (("Heading 1", 16), ("Heading 2", 12), ("Heading 3", 10.5)):
        style = doc.styles[style_name]
        style.font.name = "Aptos Display"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(BLACK)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.paragraph_format.space_after = Pt(0)
    run = header.add_run("TANK650 ENGINE  |  MEMORIA DE CÁLCULO MECÁNICO")
    _set_run_font(run, size=8.0, bold=True, color=NAVY)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_after = Pt(0)
    run = footer.add_run(f"Perfil {result['standard_profile']}  |  Motor {result['engine_version']}  |  SHA {result['input_sha256'][:16]}")
    _set_run_font(run, size=7.5, color=MID_GRAY)


def _add_cover(doc: Document, inputs: dict[str, Any], result: dict[str, Any]) -> None:
    project = inputs.get("project", {})
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(50)
    paragraph.paragraph_format.space_after = Pt(18)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("TANK650 ENGINE")
    _set_run_font(run, size=15, bold=True, color=NAVY, name="Aptos Display")

    paragraph = doc.add_paragraph(style="Title")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run("Memoria de cálculo mecánico")
    _set_run_font(run, size=27, bold=True, name="Aptos Display")

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(32)
    run = paragraph.add_run(project.get("name", "Tanque T-78"))
    _set_run_font(run, size=17, color=NAVY, name="Aptos Display")

    cover_rows = [
        ("Proyecto", project.get("name", "Tanque T-78")),
        ("Identificación", project.get("tank_tag", "T-78")),
        ("Cliente", project.get("client", "-")),
        ("Ubicación", project.get("location", "-")),
        ("Perfil de cálculo", result["standard_profile"]),
        ("Versión del motor", result["engine_version"]),
        ("Versión del formato", MEMORY_FORMAT_VERSION),
        ("Huella de entradas SHA-256", result["input_sha256"]),
        ("Estado global", result["overall_status"].replace("_", " ")),
    ]
    _add_table(doc, ["Dato", "Contenido"], cover_rows, [5.0, 12.2])

    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(18)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Documento generado automáticamente a partir del modelo de entrada y del resultado determinista del motor Python")
    _set_run_font(run, size=9.0, color=MID_GRAY)


def _build_memory(inputs: dict[str, Any], result: dict[str, Any]) -> Document:
    doc = Document()
    _configure_document(doc, result)
    props = doc.core_properties
    props.title = f"Memoria de cálculo mecánico {inputs.get('project', {}).get('tank_tag', 'T-78')}"
    props.subject = "Resultados y trazabilidad del motor TANK650 ENGINE"
    props.author = "TANK650 ENGINE"
    props.last_modified_by = "TANK650 ENGINE"
    props.keywords = f"{result['standard_profile']};{result['input_sha256']}"
    props.created = datetime(2000, 1, 1, tzinfo=timezone.utc)
    props.modified = datetime(2000, 1, 1, tzinfo=timezone.utc)

    _add_cover(doc, inputs, result)
    doc.add_page_break()

    _add_heading(doc, "Objeto y alcance", 1)
    _add_body(
        doc,
        "Esta memoria registra los datos de entrada, resultados, verificaciones y ecuaciones ejecutadas por TANK650 ENGINE para el caso indicado en la portada. El documento permite reconstruir el resultado mediante la versión del motor, el perfil de cálculo y la huella SHA-256 de las entradas.",
    )
    _add_body(
        doc,
        "El perfil implementado reproduce el caso documentado T-78 bajo API 650 duodécima edición. Los resultados identificados como REVIEW conservan datos reconstruidos de las fuentes del proyecto y requieren revisión de ingeniería antes de utilizarlos fuera de este alcance.",
    )

    _add_heading(doc, "Resumen de resultados", 1)
    _add_status_summary(doc, result)

    _add_heading(doc, "Datos generales de diseño", 1, page_break_before=True)
    geom = inputs["geometry"]
    product = inputs["product"]
    _add_key_value_table(
        doc,
        [
            ("Diámetro nominal", geom["nominal_diameter_m"], "m"),
            ("Diámetro interior", geom["internal_diameter_m"], "m"),
            ("Altura del casco", geom["shell_height_m"], "m"),
            ("Altura de líquido de diseño", geom["design_liquid_height_m"], "m"),
            ("Altura nominal de curso", geom["course_height_m"], "m"),
            ("Pendiente del fondo", geom["bottom_slope_percent"], "%"),
            ("Gravedad específica", product["specific_gravity"], "-"),
            ("Temperatura de diseño", product["design_temperature_C"], "°C"),
            ("Presión de diseño", product["design_pressure_kPa"], "kPa"),
        ],
    )

    _add_heading(doc, "Materiales", 2)
    materials = inputs["materials"]
    material_rows = []
    for key, value in materials.items():
        material_rows.append(
            (
                key.replace("_", " ").title(),
                value.get("name", "-"),
                _format_number(value.get("yield_strength_psi")),
                _format_number(value.get("design_stress_psi")),
                _format_number(value.get("hydrotest_stress_psi")),
            )
        )
    _add_table(doc, ["Componente", "Material", "Fy psi", "Sd psi", "St psi"], material_rows, [3.5, 5.0, 2.9, 2.9, 2.9], {2, 3, 4})

    _add_heading(doc, "Cursos del casco", 2)
    shell = inputs["shell"]
    shell_input_rows = [
        (
            course.get("course", index),
            _format_number(course["height_m"], 3),
            _format_number(course["thickness_mm"], 3),
            course["material"],
        )
        for index, course in enumerate(shell["courses"], start=1)
    ]
    _add_table(doc, ["Curso", "Altura m", "Espesor mm", "Material"], shell_input_rows, [2.0, 3.0, 3.4, 8.8], {0, 1, 2})

    _add_heading(doc, "Cálculo de espesores del casco", 1, page_break_before=True)
    _add_body(
        doc,
        "El motor aplica el método One Foot del perfil API650_12E_T78. El espesor de aceptación considera diseño, prueba hidrostática y espesor nominal mínimo. La utilización por presión se informa por separado para mostrar cuánto del espesor seleccionado consume la demanda calculada.",
    )
    shell_module = result["modules"]["shell"]
    shell_rows = []
    for row in shell_module["values"]["courses"]:
        shell_rows.append(
            (
                row["course"],
                f"{row['design_mm']:.4f}",
                f"{row['hydrotest_mm']:.4f}",
                f"{row['selected_mm']:.3f}",
                f"{row['utilization']:.1%}",
                f"{row['minimum_utilization']:.1%}",
                row["status"],
            )
        )
    _add_table(
        doc,
        ["Curso", "Diseño mm", "Hidro mm", "Seleccionado mm", "Utilización presión", "Utilización mínima", "Estado"],
        shell_rows,
        [1.5, 2.5, 2.5, 3.0, 3.0, 2.8, 1.9],
        {0, 1, 2, 3, 4, 5},
    )
    _add_checks(doc, "casco", shell_module)

    _add_heading(doc, "Fondo del tanque", 1, page_break_before=True)
    bottom = result["modules"]["bottom"]
    _add_key_value_table(
        doc,
        [
            ("Espesor requerido de placa central", bottom["values"]["central"]["required_mm"], "mm"),
            ("Espesor seleccionado de placa central", bottom["values"]["central"]["selected_mm"], "mm"),
            ("Espesor requerido de placa anular", bottom["values"]["annular"]["required_mm"], "mm"),
            ("Espesor seleccionado de placa anular", bottom["values"]["annular"]["selected_mm"], "mm"),
            ("Ancho requerido de placa anular", bottom["values"]["annular"]["required_width_mm"], "mm"),
            ("Ancho seleccionado de placa anular", bottom["values"]["annular"]["selected_width_mm"], "mm"),
        ],
    )
    _add_checks(doc, "fondo", bottom)

    _add_heading(doc, "Estabilidad por viento", 1)
    wind = result["modules"]["wind"]
    _add_key_value_table(
        doc,
        [
            ("Velocidad de viento", wind["values"]["velocity_m_s"], "m/s"),
            ("Presión de viento", wind["values"]["pressure_kPa"], "kPa"),
            ("Cortante", wind["values"]["shear_N"], "N"),
            ("Momento de volcamiento", wind["values"]["overturning_moment_Nm"], "N m"),
            ("Momento resistente", wind["values"]["resisting_moment_Nm"], "N m"),
            ("Requiere anclajes", wind["values"]["anchors_required"], "-"),
        ],
    )
    _add_checks(doc, "viento", wind)

    _add_heading(doc, "Análisis sísmico", 1, page_break_before=True)
    seismic = result["modules"]["seismic"]
    sv = seismic["values"]
    _add_key_value_table(
        doc,
        [
            ("Aceleración pico Sp", sv["Sp"], "g"),
            ("Ss", sv["Ss"], "g"),
            ("S1", sv["S1"], "g"),
            ("Periodo de transición Ts", sv["Ts_s"], "s"),
            ("Periodo convectivo Tc", sv["Tc_s"], "s"),
            ("Aceleración impulsiva Ai", sv["Ai"], "g"),
            ("Aceleración convectiva Ac", sv["Ac"], "g"),
            ("Cortante basal total", sv["V_N"], "N"),
            ("Momento de volcamiento Mrw", sv["Mrw_Nm"], "N m"),
            ("Relación de anclaje J", sv["J"], "-"),
            ("Clasificación", sv["anchorage_classification"].replace("_", " "), "-"),
        ],
    )
    hoop_rows = [
        (
            row["course"],
            _format_number(row["stress_kPa"], 2),
            _format_number(row["allowable_kPa"], 2),
            f"{row['utilization']:.1%}",
            _format_number(row["margin_kPa"], 2),
            row["status"],
        )
        for row in sv["hoop"]
    ]
    _add_heading(doc, "Tensión circunferencial combinada", 2)
    _add_table(doc, ["Curso", "Esfuerzo kPa", "Admisible kPa", "Utilización", "Margen kPa", "Estado"], hoop_rows, [2.0, 3.4, 3.4, 2.8, 3.2, 2.4], {0, 1, 2, 3, 4})
    _add_checks(doc, "sismo", seismic)

    _add_heading(doc, "Pernos y sillas de anclaje", 1, page_break_before=True)
    anchorage = result["modules"]["anchorage"]
    av = anchorage["values"]
    _add_key_value_table(
        doc,
        [
            ("Pernos requeridos por espaciamiento", av["required_bolts"], "unidades"),
            ("Pernos seleccionados", av["selected_bolts"], "unidades"),
            ("Diámetro nominal", av["diameter_mm"], "mm"),
            ("Espaciamiento circunferencial", av["spacing_m"], "m"),
            ("Utilización máxima", av["max_utilization"] * 100, "%"),
        ],
    )
    anchor_rows = [
        (
            row["name"],
            _format_number(row["uplift_N"], 1),
            _format_number(row["load_per_bolt_N"], 1),
            _format_number(row["stress_kPa"], 2),
            _format_number(row["allowable_kPa"], 2),
            f"{row['utilization']:.1%}",
            row["status"],
        )
        for row in av["load_cases"]
    ]
    _add_table(doc, ["Caso", "Tracción total N", "Carga por perno N", "Esfuerzo kPa", "Admisible kPa", "Utilización", "Estado"], anchor_rows, [3.4, 2.7, 2.7, 2.5, 2.5, 1.9, 1.8], {1, 2, 3, 4, 5})
    _add_checks(doc, "pernos de anclaje", anchorage)

    chairs = result["modules"]["anchor_chairs"]
    cv = chairs["values"]
    _add_heading(doc, "Silla de anclaje", 2)
    _add_key_value_table(
        doc,
        [
            ("Espesor requerido de placa superior", cv["required_top_plate_mm"], "mm"),
            ("Espesor seleccionado de placa superior", cv["top_plate_thickness_mm"], "mm"),
            ("Altura de cartela", cv["gusset_height_mm"], "mm"),
            ("Separación entre cartelas", cv["gusset_spacing_mm"], "mm"),
            ("Carga de perno", cv["bolt_load_N"], "N"),
            ("Utilización", cv["utilization"] * 100, "%"),
        ],
    )
    _add_checks(doc, "silla de anclaje", chairs)

    _add_heading(doc, "Resumen de pesos", 1, page_break_before=True)
    weights = result["modules"]["weights"]["values"]
    weight_rows = [(name.replace("_", " ").title(), _format_number(value, 0), "N") for name, value in weights["categories_N"].items()]
    weight_rows.extend(
        [
            ("Peso estructural neto", _format_number(weights["net_structural_weight_N"], 0), "N"),
            ("Peso bruto de procura", _format_number(weights["gross_procurement_weight_N"], 0), "N"),
        ]
    )
    _add_table(doc, ["Categoría", "Valor", "Unidad"], weight_rows, [10.2, 4.0, 3.0], {1})

    _add_heading(doc, "Conclusiones", 1)
    _add_body(doc, f"El estado global obtenido es {result['overall_status'].replace('_', ' ')}.")
    _add_body(
        doc,
        f"Los ocho cursos del casco cumplen los espesores de diseño, prueba hidrostática y mínimo nominal. La utilización máxima por presión es {result['summary']['shell']['max_utilization']:.1%}.",
    )
    _add_body(
        doc,
        f"La relación sísmica de anclaje J es {result['summary']['seismic']['J']:.4f}. El tanque requiere anclaje mecánico; los {result['summary']['anchorage']['selected_bolts']} pernos seleccionados y la placa superior de las sillas cumplen las verificaciones implementadas.",
    )

    _add_heading(doc, "Apéndice de trazabilidad de fórmulas", 1, page_break_before=True)
    _add_body(
        doc,
        "Cada registro incluye el identificador estable de fórmula, la referencia, la expresión, las variables de entrada y los resultados bruto y mostrado. La huella SHA-256 de la portada identifica el conjunto completo de entradas usado por el motor.",
    )
    module_labels = {
        "shell": "Casco",
        "bottom": "Fondo",
        "wind": "Viento",
        "seismic": "Sismo",
        "anchorage": "Anclaje",
        "anchor_chairs": "Sillas de anclaje",
        "weights": "Pesos",
    }
    for module_name, module in result["modules"].items():
        traces = module.get("traces", [])
        if not traces:
            continue
        _add_heading(doc, module_labels.get(module_name, module_name.replace("_", " ").title()), 2)
        for trace in traces:
            _add_trace(doc, trace)

    return doc


def _save_deterministic(doc: Document, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.working.docx")
    doc.save(temporary)
    with zipfile.ZipFile(temporary, "r") as source, zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in sorted(source.namelist()):
            source_info = source.getinfo(name)
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = source_info.external_attr
            info.create_system = 0
            output.writestr(info, source.read(name))
    temporary.unlink(missing_ok=True)
    return target


def write_calculation_memory(inputs: dict[str, Any], result: dict[str, Any], target: Path) -> Path:
    """Create a deterministic DOCX calculation memory from one engine input/result pair."""
    document = _build_memory(inputs, result)
    return _save_deterministic(document, target)

