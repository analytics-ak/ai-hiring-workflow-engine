# -*- coding: utf-8 -*-
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER
from datetime import datetime


SAPPHIRE  = colors.HexColor("#0F52BA")
DARK_NAVY = colors.HexColor("#1A2340")
GOLD      = colors.HexColor("#D4AF37")
RED       = colors.HexColor("#C0392B")
ORANGE    = colors.HexColor("#E67E22")
GREEN     = colors.HexColor("#27AE60")
LIGHT     = colors.HexColor("#F4F6FB")
BORDER    = colors.HexColor("#DDE3F0")
BLACK     = colors.HexColor("#1C1C1E")
GREY      = colors.HexColor("#7F8C8D")
WHITE     = colors.white


def get_score_color(score):
    if score >= 75:   return GREEN
    elif score >= 51: return ORANGE
    else:             return RED


def sp(n=1):
    return Spacer(1, n * 0.3 * cm)


def make_style(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10, textColor=BLACK, leading=15)
    base.update(kw)
    return ParagraphStyle(name, **base)


def generate_pdf_report(analysis_text, score, label):
    buffer = io.BytesIO()
    W = A4[0] - 4*cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    story = []
    score_color = get_score_color(score)

    # ── HEADER ────────────────────────────────────────────────────
    header = Table([[
        Paragraph("AI HIRING WORKFLOW ENGINE",
                  make_style("h", fontName="Helvetica-Bold", fontSize=16,
                             textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Resume vs JD Analysis Report",
                  make_style("s", fontSize=10, textColor=colors.HexColor("#BDD0F5"),
                             alignment=TA_CENTER)),
    ]], colWidths=[W])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), DARK_NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ]))
    story.append(header)
    story.append(sp(1))

    # ── SCORE CARD ────────────────────────────────────────────────
    score_card = Table([[
        Paragraph(f"{score}/100",
                  make_style("sc", fontName="Helvetica-Bold", fontSize=32,
                             textColor=WHITE, alignment=TA_CENTER)),
        Paragraph(label,
                  make_style("sl", fontName="Helvetica-Bold", fontSize=14,
                             textColor=WHITE, alignment=TA_CENTER)),
        Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                  make_style("sd", fontSize=9, textColor=colors.HexColor("#DDE3F0"),
                             alignment=TA_CENTER)),
    ]], colWidths=[W/3, W/3, W/3])
    score_card.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), score_color),
        ("TOPPADDING",    (0,0), (-1,-1), 16),
        ("BOTTOMPADDING", (0,0), (-1,-1), 16),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(score_card)
    story.append(sp(1.5))

    # ── ANALYSIS CONTENT ─────────────────────────────────────────
    lines = analysis_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            story.append(sp(0.5))
            continue

        if line.startswith("## "):
            text = line[3:].strip()
            bar = Table([[Paragraph(text,
                          make_style("bh", fontName="Helvetica-Bold", fontSize=12,
                                     textColor=WHITE))]], colWidths=[W])
            bar.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), SAPPHIRE),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ]))
            story.append(sp(0.5))
            story.append(bar)
            story.append(sp(0.5))

        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Paragraph(text,
                make_style("sh", fontName="Helvetica-Bold", fontSize=11,
                           textColor=DARK_NAVY, spaceBefore=8, spaceAfter=4)))

        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:].strip()
            story.append(Paragraph(f"• {text}",
                make_style("li", leftIndent=15, spaceAfter=3)))

        elif line.startswith("|") and "|" in line[1:]:
            # skip markdown table lines — render as plain text
            if not line.replace("|","").replace("-","").replace(" ",""):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                story.append(Paragraph(" | ".join(cells),
                    make_style("tr", fontSize=9, textColor=BLACK,
                               fontName="Courier", spaceAfter=2)))
        else:
            story.append(Paragraph(line,
                make_style("body", spaceAfter=4)))

    story.append(sp(2))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(sp(0.5))
    story.append(Paragraph(
        "Generated by AI Hiring Workflow Engine  |  claude-sonnet-4-5  |  Prompt Version V3",
        make_style("ft", fontSize=8, textColor=GREY, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()