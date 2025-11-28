from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .templates_loader import TemplateLoader


class PdfBuilder:
    def __init__(self, template_loader: TemplateLoader) -> None:
        self.template_loader = template_loader

    def build(self, template_name: str, context: Dict[str, str]) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
        )
        story = []
        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        normal.fontSize = 11
        heading = ParagraphStyle("Heading", parent=styles["Heading1"], alignment=1)

        rendered = self.template_loader.render(template_name, context)

        story.append(Paragraph("CLEAN DOC BOT", heading))
        story.append(Spacer(1, 12))
        for line in rendered.split("\n"):
            if line.strip():
                story.append(Paragraph(line, normal))
                story.append(Spacer(1, 8))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal))
        story.append(Paragraph("Подпись: _____________________", normal))

        def add_logo(canvas_obj: canvas.Canvas, doc_obj: SimpleDocTemplate) -> None:
            canvas_obj.saveState()
            canvas_obj.setFont("Helvetica-Bold", 10)
            canvas_obj.drawString(doc_obj.width + doc_obj.leftMargin - 100, doc_obj.height + doc_obj.topMargin - 10, "CLEAN DOC BOT")
            canvas_obj.restoreState()

        doc.build(story, onFirstPage=add_logo, onLaterPages=add_logo)
        buffer.seek(0)
        return buffer

    @staticmethod
    def ensure_template_directory(path: str) -> Path:
        directory = Path(path)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
