"""Gera o PDF do Relatório Final diagramado de 4 a 6 páginas a partir de Relatorio_Final.md."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Relatorio_Final.md"
OUTPUT = ROOT / "Relatorio_Final_UPC.pdf"

NAVY = colors.HexColor("#173447")
ACCENT = colors.HexColor("#087A92")
TEXT = colors.HexColor("#263745")
MUTED = colors.HexColor("#5A6B78")
LIGHT = colors.HexColor("#EDF4F7")
BORDER = colors.HexColor("#C9D7DE")


def fonts() -> None:
    pdfmetrics.registerFont(TTFont("SegoeUI", r"C:\Windows\Fonts\segoeui.ttf"))
    pdfmetrics.registerFont(TTFont("SegoeUI-Bold", r"C:\Windows\Fonts\segoeuib.ttf"))
    pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))
    pdfmetrics.registerFontFamily(
        "SegoeUI", normal="SegoeUI", bold="SegoeUI-Bold"
    )


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName="SegoeUI-Bold",
            fontSize=18, leading=22, textColor=NAVY, alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "ReportMeta", parent=base["Normal"], fontName="SegoeUI",
            fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=2,
        ),
        "heading": ParagraphStyle(
            "ReportHeading", parent=base["Heading2"], fontName="SegoeUI-Bold",
            fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=11,
            spaceAfter=4, keepWithNext=True,
        ),
        "subheading": ParagraphStyle(
            "ReportSubheading", parent=base["Heading3"], fontName="SegoeUI-Bold",
            fontSize=10, leading=13, textColor=ACCENT, spaceBefore=7,
            spaceAfter=3, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ReportBody", parent=base["BodyText"], fontName="SegoeUI",
            fontSize=8.5, leading=12.2, textColor=TEXT, spaceAfter=4,
        ),
        "list": ParagraphStyle(
            "ReportList", parent=base["BodyText"], fontName="SegoeUI",
            fontSize=8.5, leading=12.2, textColor=TEXT, leftIndent=14,
            firstLineIndent=-10, spaceAfter=3,
        ),
        "cell": ParagraphStyle(
            "ReportCell", parent=base["Normal"], fontName="SegoeUI",
            fontSize=7.2, leading=9.5, textColor=TEXT,
        ),
        "cell_head": ParagraphStyle(
            "ReportCellHead", parent=base["Normal"], fontName="SegoeUI-Bold",
            fontSize=7.2, leading=9.5, textColor=colors.white,
        ),
        "code": ParagraphStyle(
            "ReportCode", parent=base["Normal"], fontName="Consolas",
            fontSize=6.8, leading=8.5, textColor=TEXT,
        ),
    }


def inline(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(
        r"`([^`]+)`",
        lambda m: f'<font face="Consolas" color="#075F78">{m.group(1)}</font>',
        value,
    )
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"<u>\1</u>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", value)
    return value


def make_table(lines: list[str], st: dict[str, ParagraphStyle], width: float) -> Table:
    parsed = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [parsed[0], *parsed[2:]]
    count = len(rows[0])
    
    if count == 2:
        col_widths = [width * 0.35, width * 0.65]
    elif count == 3:
        col_widths = [width * 0.22, width * 0.25, width * 0.53]
    elif count == 4:
        col_widths = [width * 0.18, width * 0.22, width * 0.32, width * 0.28]
    elif count == 7:
        # Tabela completa do DeepEval
        col_widths = [
            width * 0.12,  # Caso
            width * 0.17,  # Categoria
            width * 0.14,  # AR
            width * 0.14,  # Faith
            width * 0.14,  # Conf
            width * 0.10,  # Res
            width * 0.19,  # Revisão
        ]
    else:
        col_widths = [width / count] * count

    data = []
    for row_idx, row in enumerate(rows):
        data.append([
            Paragraph(inline(cell), st["cell_head"] if row_idx == 0 else st["cell"])
            for cell in row
        ])
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("BOX", (0, 0), (-1, -1), 0.45, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def parse_markdown(source: str, width: float) -> list:
    st = styles()
    lines = source.splitlines()
    story: list = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), st["body"]))
            paragraph.clear()

    index = 0
    in_code_block = False
    code_lines: list[str] = []

    while index < len(lines):
        raw = lines[index]
        line = raw.strip()

        if line.startswith("```"):
            flush()
            if in_code_block:
                in_code_block = False
                story.append(Spacer(1, 2))
                story.append(Preformatted("\n".join(code_lines), st["code"]))
                story.append(Spacer(1, 4))
                code_lines.clear()
            else:
                in_code_block = True
                code_lines.clear()
            index += 1
            continue

        if in_code_block:
            code_lines.append(raw)
            index += 1
            continue

        if not line:
            flush()
            index += 1
            continue

        if line.startswith("| "):
            flush()
            block = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index])
                index += 1
            story.append(Spacer(1, 3))
            story.append(make_table(block, st, width))
            story.append(Spacer(1, 5))
            continue

        if line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), st["title"]))
            story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=8))
            index += 1
            continue

        if line.startswith("## "):
            flush()
            story.append(Paragraph(inline(line[3:]), st["heading"]))
            index += 1
            continue

        if line.startswith("### "):
            flush()
            story.append(Paragraph(inline(line[4:]), st["subheading"]))
            index += 1
            continue

        if re.match(r"^\d+\. ", line):
            flush()
            story.append(Paragraph(inline(line), st["list"]))
            index += 1
            continue

        if line.startswith("- "):
            flush()
            story.append(Paragraph("• " + inline(line[2:]), st["list"]))
            index += 1
            continue

        if index < 8 and (raw.endswith("  ") or "Região:" in line or "Estado avaliado:" in line or "Parecer:" in line):
            flush()
            story.append(Paragraph(inline(line), st["meta"]))
            index += 1
            continue

        paragraph.append(line)
        index += 1

    flush()
    return story


class NumberedCanvas:
    """Dois passos para numerar 'Página X de Y'."""
    def __init__(self, *args, **kwargs):
        from reportlab.pdfgen import canvas
        self.canvas_class = canvas.Canvas

    def __call__(self, *args, **kwargs):
        c = self.canvas_class(*args, **kwargs)
        orig_showPage = c.showPage
        orig_save = c.save
        c._saved_page_states = []

        def showPage():
            c._saved_page_states.append(dict(c.__dict__))
            c._startPage()

        def save():
            num_pages = len(c._saved_page_states)
            for state in c._saved_page_states:
                c.__dict__.update(state)
                draw_header_footer(c, num_pages)
                orig_showPage()
            orig_save()

        c.showPage = showPage
        c.save = save
        return c


def draw_header_footer(canvas, total_pages: int) -> None:
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(ACCENT)
    canvas.rect(0, page_height - 6 * mm, page_width, 6 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("SegoeUI", 7.5)
    canvas.drawString(16 * mm, page_height - 13 * mm, "UNIVERSIDADE DE PEDRA CLARA  |  RELATÓRIO TÉCNICO FINAL — DESAFIO 2")
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(16 * mm, 14 * mm, page_width - 16 * mm, 14 * mm)
    canvas.drawString(16 * mm, 10 * mm, "AgentCore Harness & DeepEval  |  Configuração v39  |  25/09/2026")
    canvas.drawRightString(page_width - 16 * mm, 10 * mm, f"Página {canvas._pageNumber} de {total_pages}")
    canvas.restoreState()


def main() -> None:
    fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=18 * mm, bottomMargin=17 * mm,
        title="Relatório Final — Desafio 2: Assistente Acadêmico UPC",
        author="Equipe UPC BSI",
        subject="Avaliação em duas frentes, AgentCore Harness, DeepEval e Red Team",
    )
    source = SOURCE.read_text(encoding="utf-8")
    story = parse_markdown(source, doc.width)
    doc.build(story, canvasmaker=NumberedCanvas())
    print(f"Sucesso: {OUTPUT}")


if __name__ == "__main__":
    main()
