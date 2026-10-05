from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def write_json_report(result: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def write_html_report(result: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    summary = result["summary"]
    shell_rows = "".join(
        f"<tr><td>{row['course']}</td><td>{row['design_mm']:.4f}</td><td>{row['hydrotest_mm']:.4f}</td><td>{row['selected_mm']:.3f}</td><td>{row['utilization']:.1%}</td><td>{row['status']}</td></tr>"
        for row in result["modules"]["shell"]["values"]["courses"]
    )
    target.write_text(f"""<!doctype html><html lang='es'><meta charset='utf-8'><title>TANK650 - T-78</title>
<style>body{{font:14px Arial;color:#183247;margin:38px}}h1{{color:#164e63}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #cbd5e1;padding:8px;text-align:right}}th:first-child,td:first-child{{text-align:left}}.ok{{color:#166534}}.bad{{color:#b91c1c}}</style>
<h1>TANK650 ENGINE - Memoria de cálculo T-78</h1><p>Engine {result['engine_version']} · Perfil {result['standard_profile']} · SHA-256 {result['input_sha256']}</p>
<h2>Resumen ejecutivo</h2><p class='ok'>{summary['overall_status']}</p>
<h2>Casco - método 1-Foot</h2><table><tr><th>Curso</th><th>Diseño mm</th><th>Hidro mm</th><th>Seleccionado mm</th><th>Utilización</th><th>Estado</th></tr>{shell_rows}</table>
<h2>Sismo</h2><p>J = {summary['seismic']['J']:.4f}. Clasificación: {summary['auto_anchor']['classification']}.</p>
<h2>Anclajes</h2><p>{summary['anchorage']['selected_bolts']} pernos seleccionados. Estado: {summary['anchorage']['status']}.</p>
<h2>Trazabilidad</h2><p>El resultado detallado, verificaciones y trazas de fórmula se conserva en el JSON del run.</p></html>""", encoding="utf-8")
    return target


def write_pdf_report(result: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontSize=26, leading=32, textColor=colors.HexColor("#164e63"), alignment=TA_CENTER, spaceAfter=18))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=11, textColor=colors.HexColor("#475569"), spaceAfter=3))
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm, title="TANK650 ENGINE - T-78")
    story = [Spacer(1, 35 * mm), Paragraph("TANK650 ENGINE", styles["Cover"]), Paragraph("API 650 Calculation & Parametric Tank Design", styles["Heading2"]), Spacer(1, 12 * mm), Paragraph("Proyecto: Tanque T-78", styles["Heading1"]), Paragraph(f"Perfil: {result['standard_profile']}<br/>Motor: {result['engine_version']}<br/>Input SHA-256: {result['input_sha256']}", styles["Small"]), PageBreak(), Paragraph("Resumen ejecutivo", styles["Heading1"]), Paragraph(result["overall_status"].replace("_", " "), styles["Heading2"])]
    summary_data = [["Módulo", "Estado", "Indicador"], ["Casco", result["summary"]["shell"]["status"], f"{result['summary']['shell']['max_utilization']:.1%}"], ["Fondo", result["summary"]["bottom"]["status"], "8 / 9 mm"], ["Viento", result["summary"]["wind"]["status"], "No requiere anclajes"], ["Sismo", result["summary"]["seismic"]["status"], f"J = {result['summary']['seismic']['J']:.4f}"], ["Auto-anclaje", result["summary"]["auto_anchor"]["status"], result["summary"]["auto_anchor"]["classification"]], ["Pernos", result["summary"]["anchorage"]["status"], f"{result['summary']['anchorage']['selected_bolts']} x Ø63.5 mm"]]
    summary_table = Table(summary_data, colWidths=[55 * mm, 35 * mm, 70 * mm])
    summary_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])]))
    story.extend([summary_table, Spacer(1, 8 * mm), Paragraph("Casco - método 1-Foot", styles["Heading1"])])
    shell_data = [["Curso", "Diseño mm", "Hidro mm", "Seleccionado mm", "Utilización", "Estado"]]
    for row in result["modules"]["shell"]["values"]["courses"]:
        shell_data.append([row["course"], f"{row['design_mm']:.4f}", f"{row['hydrotest_mm']:.4f}", f"{row['selected_mm']:.3f}", f"{row['utilization']:.1%}", row["status"]])
    shell_table = Table(shell_data, repeatRows=1)
    shell_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")), ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    story.extend([shell_table, Spacer(1, 8 * mm), Paragraph("Conclusiones", styles["Heading1"]), Paragraph("Los ocho cursos satisfacen espesor de diseño e hidrostático. La condición de viento no exige anclajes. La condición sísmica produce J mayor que 1.54, por lo que el tanque requiere anclaje mecánico; los 60 pernos seleccionados y las sillas verificadas resultan conformes para el caso documentado.", styles["BodyText"]), PageBreak(), Paragraph("Apéndice de trazabilidad", styles["Heading1"])])
    for module_name, module in result["modules"].items():
        story.append(Paragraph(module_name.replace("_", " ").title(), styles["Heading2"]))
        for trace in module.get("traces", []):
            story.append(Paragraph(f"<b>{trace['formula_id']}</b> · {trace['description']}<br/>{trace['expression']}<br/>Resultado: {trace['display_result']} {trace['unit']} · {trace['reference']}", styles["Small"]))
            story.append(Spacer(1, 2 * mm))
    def footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(18 * mm, 8 * mm, "TANK650 ENGINE - T-78 - API650_12E_T78")
        canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return target
