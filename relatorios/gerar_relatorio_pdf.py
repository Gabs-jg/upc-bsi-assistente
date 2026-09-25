"""Gera o PDF revisável do relatório preliminar a partir do Markdown ao lado."""

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
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).with_name("relatorio_preliminar_upc_2026-09-23.md")
OUTPUT = ROOT / "output" / "pdf" / "relatorio_preliminar_upc_2026-09-23.pdf"

NAVY = colors.HexColor("#173447")
ACCENT = colors.HexColor("#087A92")
TEXT = colors.HexColor("#263745")
MUTED = colors.HexColor("#5A6B78")
LIGHT = colors.HexColor("#EDF4F7")
BORDER = colors.HexColor("#C9D7DE")


def fonts() -> None:
    pdfmetrics.registerFont(TTFont("SegoeUI", r"C:\Windows\Fonts\segoeui.ttf"))
    pdfmetrics.registerFont(TTFont("SegoeUI-Bold", r"C:\Windows\Fonts\segoeuib.ttf"))
    pdfmetrics.registerFontFamily(
        "SegoeUI", normal="SegoeUI", bold="SegoeUI-Bold"
    )


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], fontName="SegoeUI-Bold",
            fontSize=21, leading=26, textColor=NAVY, alignment=TA_LEFT,
            spaceAfter=11,
        ),
        "meta": ParagraphStyle(
            "ReportMeta", parent=base["Normal"], fontName="SegoeUI",
            fontSize=8.7, leading=13, textColor=MUTED, spaceAfter=1,
        ),
        "heading": ParagraphStyle(
            "ReportHeading", parent=base["Heading2"], fontName="SegoeUI-Bold",
            fontSize=12.3, leading=16, textColor=NAVY, spaceBefore=14,
            spaceAfter=6, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ReportBody", parent=base["BodyText"], fontName="SegoeUI",
            fontSize=9.1, leading=13.3, textColor=TEXT, spaceAfter=5,
        ),
        "list": ParagraphStyle(
            "ReportList", parent=base["BodyText"], fontName="SegoeUI",
            fontSize=9.1, leading=13.3, textColor=TEXT, leftIndent=16,
            firstLineIndent=-13, spaceAfter=4,
        ),
        "cell": ParagraphStyle(
            "ReportCell", parent=base["Normal"], fontName="SegoeUI",
            fontSize=8.0, leading=11, textColor=TEXT,
        ),
        "cell_head": ParagraphStyle(
            "ReportCellHead", parent=base["Normal"], fontName="SegoeUI-Bold",
            fontSize=8.0, leading=10.7, textColor=colors.white,
        ),
    }


def inline(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(
        r"`([^`]+)`",
        lambda m: f'<font face="Courier" color="#075F78">{m.group(1)}</font>',
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def make_table(lines: list[str], st: dict[str, ParagraphStyle], width: float) -> Table:
    parsed = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [parsed[0], *parsed[2:]]
    count = len(rows[0])
    if count == 2:
        col_widths = [width * 0.33, width * 0.67]
    elif count == 3:
        col_widths = [width * 0.24, width * 0.48, width * 0.28]
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
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
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
            story.append(Spacer(1, 8))
            continue
        if line.startswith("# "):
            flush()
            story.append(Spacer(1, 8))
            story.append(Paragraph(inline(line[2:]), st["title"]))
            story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))
            index += 1
            continue
        if line.startswith("## "):
            flush()
            story.append(Paragraph(inline(line[3:]), st["heading"]))
            index += 1
            continue
        if re.match(r"^\d+\. ", line):
            flush()
            story.append(Paragraph(inline(line), st["list"]))
            index += 1
            continue
        if line.startswith("- "):
            flush()
            story.append(Paragraph("- " + inline(line[2:]), st["list"]))
            index += 1
            continue
        if index < 6 and raw.endswith("  "):
            flush()
            story.append(Paragraph(inline(line), st["meta"]))
            index += 1
            continue
        paragraph.append(line)
        index += 1
    flush()
    return story


def draw_page(canvas, doc) -> None:
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(ACCENT)
    canvas.rect(0, page_height - 8 * mm, page_width, 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("SegoeUI", 7.7)
    canvas.drawString(19 * mm, page_height - 16 * mm, "UPC  |  RELATÓRIO PRELIMINAR")
    canvas.setStrokeColor(BORDER)
    canvas.line(19 * mm, 18 * mm, page_width - 19 * mm, 18 * mm)
    canvas.drawString(19 * mm, 13 * mm, "Versão 0.2  |  23/09/2026  |  Base para revisão")
    canvas.drawRightString(page_width - 19 * mm, 13 * mm, f"Página {doc.page}")
    canvas.restoreState()


def main() -> None:
    fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=19 * mm, rightMargin=19 * mm,
        topMargin=21 * mm, bottomMargin=20 * mm,
        title="Relatório preliminar do assistente acadêmico UPC",
        author="Projeto UPC - relatório de andamento",
        subject="Estado do assistente acadêmico, RAG e avaliação",
    )
    source = SOURCE.read_text(encoding="utf-8")
    story = parse_markdown(source, doc.width)
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(OUTPUT)


if __name__ == "__main__":
    main()
