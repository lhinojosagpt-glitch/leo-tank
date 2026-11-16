from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\Leoncio\Desktop\tank-leo")
SHOT = ROOT / ".codex-tmp" / "functionality-report" / "screenshots"
OUTPUT = ROOT / "output" / "Reporte_Funcionalidad_TANK650_T160MB.docx"

BLUE = "014BA0"
MID_BLUE = "1466C3"
LIGHT_BLUE = "EAF3FC"
INK = "17324D"
MUTED = "5E7488"
GREEN = "16835B"
GREEN_BG = "E6F5EF"
AMBER = "986500"
AMBER_BG = "FFF4D6"
RED = "B42318"
RED_BG = "FDECEA"
WHITE = "FFFFFF"
GRID = "C9D8E6"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def margins(cell, top=90, start=110, bottom=90, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
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


def set_cell_border(cell, color=GRID, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        elem = borders.find(tag)
        if elem is None:
            elem = OxmlElement(f"w:{edge}")
            borders.append(elem)
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), size)
        elem.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_alt_text(shape, title, description):
    doc_pr = shape._inline.docPr
    doc_pr.set("title", title)
    doc_pr.set("descr", description)


def add_field(paragraph, instruction):
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char, instr, sep, text, end])


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)


def add_status_box(doc, label, value, fill, color):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(7.6)
    for cell in table.rows[0].cells:
        margins(cell, 110, 150, 110, 150)
        set_cell_border(cell, fill)
    shade(table.cell(0, 0), fill)
    shade(table.cell(0, 1), fill)
    p = table.cell(0, 0).paragraphs[0]
    r = p.add_run(label.upper())
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(color)
    p = table.cell(0, 1).paragraphs[0]
    r = p.add_run(value)
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(color)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_evidence(doc, number, filename, title, description, observation=None):
    heading = add_heading(doc, f"Evidencia {number}  {title}", 1)
    heading.paragraph_format.page_break_before = True
    p = doc.add_paragraph(description)
    p.paragraph_format.space_after = Pt(8)
    path = SHOT / filename
    run = doc.add_paragraph().add_run()
    shape = run.add_picture(str(path), width=Inches(7.30))
    set_alt_text(shape, title, description)
    run._parent.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.add_run(f"Figura {number}. {title}")
    if observation:
        table = doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        shade(cell, AMBER_BG)
        set_cell_border(cell, "E7C66A")
        margins(cell, 100, 140, 100, 140)
        p = cell.paragraphs[0]
        r = p.add_run("Observación de auditoría  ")
        r.bold = True
        r.font.color.rgb = RGBColor.from_string(AMBER)
        p.add_run(observation)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        shade(cell, BLUE)
        margins(cell)
        set_cell_border(cell, BLUE)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(header)
        r.bold = True
        r.font.color.rgb = RGBColor.from_string(WHITE)
        if widths:
            cell.width = Inches(widths[idx])
    set_repeat_table_header(table.rows[0])
    for row_idx, row in enumerate(rows):
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            shade(cells[idx], WHITE if row_idx % 2 == 0 else "F5F8FB")
            margins(cells[idx])
            set_cell_border(cells[idx])
            cells[idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cells[idx].paragraphs[0]
            p.add_run(str(value))
            if widths:
                cells[idx].width = Inches(widths[idx])
    return table


doc = Document()
section = doc.sections[0]
section.orientation = WD_ORIENT.LANDSCAPE
section.page_width = Inches(11.69)
section.page_height = Inches(8.27)
section.top_margin = Inches(0.52)
section.bottom_margin = Inches(0.48)
section.left_margin = Inches(0.58)
section.right_margin = Inches(0.58)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Aptos"
normal.font.size = Pt(9.5)
normal.font.color.rgb = RGBColor.from_string(INK)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.05

for style_name, size, color in (("Title", 30, BLUE), ("Heading 1", 19, BLUE), ("Heading 2", 13, MID_BLUE), ("Heading 3", 10.5, INK)):
    style = styles[style_name]
    style.font.name = "Aptos Display"
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor.from_string(color)
    style.font.bold = True

styles["Heading 1"].paragraph_format.space_before = Pt(0)
styles["Heading 1"].paragraph_format.space_after = Pt(8)
styles["Heading 2"].paragraph_format.space_before = Pt(9)
styles["Heading 2"].paragraph_format.space_after = Pt(5)
styles["Caption"].font.name = "Aptos"
styles["Caption"].font.size = Pt(8.5)
styles["Caption"].font.italic = True
styles["Caption"].font.color.rgb = RGBColor.from_string(MUTED)

core = doc.core_properties
core.title = "Reporte de funcionalidad de TANK650 ENGINE T 160MB"
core.subject = "Auditoría funcional básica con evidencias de interfaz"
core.author = "Leoncio Hinojosa"
core.keywords = "TANK650, T-160MB, funcionalidad, auditoría, evidencias"
core.comments = "Generado a partir de una sesión funcional de la aplicación local."

header = section.header
p = header.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run("TANK650 ENGINE  |  REPORTE DE FUNCIONALIDAD")
r.font.name = "Aptos"
r.font.size = Pt(8)
r.font.bold = True
r.font.color.rgb = RGBColor.from_string(MID_BLUE)

footer = section.footer
p = footer.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("T-160MB  •  Autor Leoncio Hinojosa  •  Página ")
r.font.size = Pt(8)
r.font.color.rgb = RGBColor.from_string(MUTED)
add_field(p, "PAGE")

# Cover
cover = doc.add_table(rows=1, cols=2)
cover.alignment = WD_TABLE_ALIGNMENT.CENTER
cover.autofit = False
left, right = cover.rows[0].cells
left.width = Inches(1.2)
right.width = Inches(8.8)
shade(left, BLUE)
shade(right, "F3F8FD")
for cell in (left, right):
    set_cell_border(cell, WHITE, "0")
    margins(cell, 300, 260, 300, 260)
left.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
p = left.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("T6")
r.bold = True
r.font.size = Pt(30)
r.font.color.rgb = RGBColor.from_string(WHITE)

p = right.paragraphs[0]
p.paragraph_format.space_before = Pt(18)
r = p.add_run("REPORTE DE FUNCIONALIDAD")
r.bold = True
r.font.size = Pt(12)
r.font.color.rgb = RGBColor.from_string(MID_BLUE)
p = right.add_paragraph()
p.style = styles["Title"]
p.add_run("TANK650 ENGINE T 160MB")
p = right.add_paragraph()
r = p.add_run("Auditoría básica de la interfaz y evidencias del motor de cálculo")
r.font.size = Pt(15)
r.font.color.rgb = RGBColor.from_string(INK)
p = right.add_paragraph()
p.paragraph_format.space_before = Pt(32)
p.add_run("Autor\n").bold = True
p.add_run("Leoncio Hinojosa")
p = right.add_paragraph()
p.add_run("Fecha de evaluación\n").bold = True
p.add_run("20 de octubre de 2026")
p = right.add_paragraph()
p.add_run("Entorno\n").bold = True
p.add_run("Aplicación local en http://127.0.0.1:8000  |  Motor Python 2.0.0")

doc.add_page_break()
add_heading(doc, "Resumen ejecutivo", 1)
p = doc.add_paragraph()
p.add_run("Resultado general  ").bold = True
p.add_run("La aplicación completó el flujo de cálculo de borrador y presentó el estado ")
r = p.add_run("PASS WITH MECHANICAL ANCHORAGE")
r.bold = True
r.font.color.rgb = RGBColor.from_string(GREEN)
p.add_run(". La navegación, edición de entradas, visualización 3D, resultados del casco, verificaciones sísmicas, trazabilidad, resultados globales, variantes e historial fueron accesibles desde la interfaz.")

add_status_box(doc, "Estado", "Funcional con observaciones de presentación y contexto", GREEN_BG, GREEN)

add_heading(doc, "Datos de la ejecución observada", 2)
add_table(
    doc,
    ["Campo", "Valor", "Evidencia"],
    [
        ("Proyecto", "T-160MB", "Cabecera de la aplicación"),
        ("Escenario", "BASELINE", "Cabecera de la aplicación"),
        ("Revisión", "BORRADOR", "No se guardó una nueva revisión"),
        ("Motor", "2.0.0", "Barra de estado"),
        ("Huella del cálculo", "d13b8377b49f…", "Cálculo de borrador completado"),
        ("Resultado global", "PASS WITH MECHANICAL ANCHORAGE", "Resultados globales"),
        ("J sísmico", "2.4059", "API 650 Annex E"),
        ("Utilización máxima de casco", "99.6 % en Course 6", "Resultados del casco"),
    ],
    [1.9, 3.0, 5.1],
)

add_heading(doc, "Alcance y criterio", 2)
add_bullets(doc, [
    "Prueba funcional de caja negra sobre la interfaz web local y el cálculo ya cargado en memoria.",
    "Validación visual de navegación, entradas, resultados, verificaciones, modelo 3D, trazabilidad, variantes e historial.",
    "No constituye certificación normativa ni recalculo independiente de ingeniería.",
    "No se guardaron revisiones ni se ejecutaron lotes de variantes para evitar mutaciones de la base de datos durante la auditoría.",
    "La descarga de Memoria Word no se verificó porque el navegador no obtuvo autorización de descarga en la sesión.",
])

doc.add_page_break()
add_heading(doc, "Matriz de cobertura funcional", 1)
rows = [
    ("Carga del ejemplo", "Disponible", "Botón T-160MB visible; no se recargó para conservar el cálculo observado."),
    ("Edición de entradas", "Operativa", "Campos numéricos y de texto disponibles por disciplina."),
    ("Ejecución de cálculo", "Operativa", "Borrador calculado; motor 2.0.0 y huella visibles."),
    ("Modelo 3D", "Operativa", "8 cursos, 24 planchas por curso, fondo, domo y 60 anclajes."),
    ("Casco", "Operativa", "8 cursos con espesores, utilización y estado PASS."),
    ("Fondo", "Parcial", "Verificaciones visibles; la pestaña Resultados aparece vacía."),
    ("Viento", "Operativa", "Resultados y verificación disponibles en el cálculo auditado."),
    ("Sismo", "Operativa", "J, esfuerzos por curso y verificaciones disponibles."),
    ("Anclaje", "Operativa", "Resultados y verificaciones accesibles."),
    ("Design Assistant", "Condicionada", "Explica el FAIL; exige revisión guardada para estudios trazables."),
    ("Trazabilidad", "Operativa con observación", "Ecuación, referencia, raw e inputs visibles; aceptación conserva contexto de placa."),
    ("Resultados globales", "Operativa", "Resumen por disciplina y resultado global coherente."),
    ("Variantes", "Configurable", "Permite definir parámetros; lote no ejecutado en esta auditoría."),
    ("Historial", "Operativa", "Revisiones previas e inmutabilidad visibles."),
    ("Memoria Word", "No verificada", "Botón presente; descarga no autorizada en la sesión."),
]
add_table(doc, ["Función", "Estado", "Resultado de auditoría"], rows, [2.0, 1.45, 6.55])

add_evidence(doc, 1, "01_centro_diseno.png", "Centro de diseño", "Vista de inicio con identidad T-160MB, estado de borrador, accesos por disciplina y trazas del motor.")
add_evidence(doc, 2, "02_parametros_proyecto.png", "Parámetros generales del proyecto", "Módulo de proyecto para revisar y modificar los datos generales que alimentan el cálculo.")
add_evidence(doc, 3, "03_modelo_3d.png", "Modelo físico y navegador de entidades", "Visualización 3D del tanque con navegador jerárquico de cursos, planchas, fondo, techo geodésico y anclajes.")
add_evidence(doc, 4, "04_casco_resultados.png", "Resultados del casco", "Tabla de los ocho cursos con espesores requeridos, espesores seleccionados, utilización y estado.")
add_evidence(doc, 5, "05_fondo_resultados_vacios.png", "Resultados del fondo", "La pestaña Resultados del módulo Fondo fue abierta después de un cálculo completado.", "El panel de datos permanece vacío aunque el módulo sí dispone de verificaciones calculadas. Se recomienda mostrar los resultados base o retirar esta pestaña si no corresponde al diseño funcional.")
add_evidence(doc, 6, "06_fondo_verificaciones.png", "Verificaciones del fondo", "La pestaña Verificaciones confirma el cálculo del espesor nominal de placa central y anular, ambos en estado PASS.")
add_evidence(doc, 7, "07_sismo_verificaciones.png", "Verificaciones sísmicas", "El módulo sísmico presenta demanda, capacidad, utilización y estado para estabilidad autoanclada y esfuerzos de aro por curso.", "La estabilidad autoanclada falla con 156.23 % de utilización; la lógica global deriva correctamente a anclaje mecánico.")
add_evidence(doc, 8, "08_design_assistant.png", "Design Assistant", "Asistente determinista que explica la causa del incumplimiento y conserva la decisión final en el usuario.", "En un borrador, el asistente solicita guardar y calcular una revisión antes de ejecutar estudios con trazabilidad de run_id. Es un control coherente, pero conviene explicitarlo antes de abrir el asistente.")
add_evidence(doc, 9, "09_inspector_calculo.png", "Inspector de cálculo", "Trazabilidad del J sísmico con ecuación, referencia normativa, valor raw y variables de entrada.", "El bloque Aceptación muestra espesor y utilización de la placa C01-P01 mientras la traza activa es el J sísmico. Se recomienda desacoplar la selección geométrica de la aceptación del resultado inspeccionado.")
add_evidence(doc, 10, "10_resultados_globales.png", "Resultados globales", "Consolidación ejecutiva por disciplina y estado general PASS WITH MECHANICAL ANCHORAGE.")
add_evidence(doc, 11, "11_variantes.png", "Configuración de variantes", "Definición de escenarios paramétricos para aceleración pico y gravedad específica, con ejecución por lote disponible.")
add_evidence(doc, 12, "12_historial.png", "Historial inmutable", "Registro de revisiones y ejecuciones previas que aporta trazabilidad de cambios y resultados.")

doc.add_page_break()
add_heading(doc, "Hallazgos y recomendaciones", 1)
add_status_box(doc, "Prioridad media", "Resultados del fondo sin contenido visible", AMBER_BG, AMBER)
p = doc.add_paragraph("Después de un cálculo completado, Fondo › Resultados presenta un panel vacío, mientras Fondo › Verificaciones contiene dos comprobaciones válidas. Esto puede interpretarse como ausencia de cálculo.")
p.add_run(" Recomendación  ").bold = True
p.add_run("Mostrar las magnitudes calculadas del fondo, reutilizar la tabla de verificaciones como resumen o suprimir la pestaña cuando no exista un conjunto de resultados independiente.")

add_status_box(doc, "Prioridad media", "Aceptación contextual inconsistente en el inspector", AMBER_BG, AMBER)
p = doc.add_paragraph("La traza de J sísmico presenta correctamente ecuación e inputs, pero el bloque de aceptación conserva el espesor, utilización y PASS de la placa C01-P01 seleccionada en el modelo.")
p.add_run(" Recomendación  ").bold = True
p.add_run("Vincular demanda, capacidad, utilización y estado al resultado inspeccionado; mostrar la selección 3D en un bloque separado.")

add_status_box(doc, "Prioridad baja", "Diferencia entre etiquetas visuales e identificadores internos", LIGHT_BLUE, BLUE)
p = doc.add_paragraph("La interfaz muestra T-160MB y API650_12E_T160MB, mientras la compatibilidad interna puede conservar identificadores históricos T78.")
p.add_run(" Recomendación  ").bold = True
p.add_run("Documentar el alias interno en la API y evitar exponerlo en archivos entregables o mensajes de usuario.")

add_heading(doc, "Riesgos no cubiertos", 2)
add_bullets(doc, [
    "Persistencia de una nueva revisión y validación posterior del contenido guardado.",
    "Ejecución real de un lote de variantes y comparación cuantitativa entre escenarios.",
    "Descarga y revisión documental de la Memoria Word generada desde la interfaz.",
    "Validación normativa independiente de todas las ecuaciones del motor Python.",
    "Pruebas de concurrencia, seguridad, rendimiento, respaldo y recuperación de la base de datos.",
])

add_heading(doc, "Conclusión", 2)
p = doc.add_paragraph()
p.add_run("La aplicación es funcional para demostración y revisión de ingeniería asistida. ").bold = True
p.add_run("El flujo observado integra inputs editables, motor de cálculo Python, representación 3D, resultados por disciplina, verificaciones, explicación del incumplimiento, trazabilidad, variantes e historial. Antes de una aceptación operativa se recomienda resolver los dos hallazgos de prioridad media y completar las pruebas de persistencia, variantes y generación documental.")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
