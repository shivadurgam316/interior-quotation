from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from django.conf import settings


def generate_quotation_pdf(quotation):
    output_dir = Path(settings.MEDIA_ROOT) / "quotations"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{quotation['quotation_number']}.pdf"
    path = output_dir / filename

    company = quotation.get("company") or {}

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        fontSize=19,
        leading=22,
        textColor=colors.HexColor("#7a1717"),
        spaceAfter=3,
    )

    small = ParagraphStyle(
        "SmallCustom",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
    )

    normal = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
    )

    story = []

    header_data = [
        [
            Paragraph(
                f"<b>{company.get('company_name', 'INTERIOR PROJECTS')}</b><br/>"
                f"{company.get('address', '')}<br/>"
                f"{company.get('phone', '')}",
                title,
            ),
            Paragraph(
                "<b>QUOTATION</b><br/><br/>"
                f"Date: {quotation['quotation_date']}<br/>"
                f"Quote No: {quotation['quotation_number']}",
                ParagraphStyle(
                    "Right",
                    parent=normal,
                    alignment=2,
                    fontSize=10,
                ),
            ),
        ]
    ]

    header = Table(header_data, colWidths=[115 * mm, 60 * mm])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#999999")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 7 * mm))

    customer_text = (
        f"<b>To,</b><br/>"
        f"{quotation['customer_name']}<br/>"
        f"{str(quotation.get('customer_address') or '').replace(chr(10), '<br/>')}<br/>"
        f"Ph No: {quotation['whatsapp_number']}"
    )

    customer_box = Table(
        [[Paragraph(customer_text, normal)]],
        colWidths=[175 * mm],
    )
    customer_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f2f2")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(customer_box)
    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "Dear Sir/Mam,<br/><br/>"
            "Thank you for your valuable inquiry. "
            "We are pleased to quote as below!",
            normal,
        )
    )
    story.append(Spacer(1, 5 * mm))

    table_data = [
        [
            "#",
            "DESCRIPTION",
            "QTY",
            "PRICE",
            "TOTAL",
        ]
    ]

    for index, item in enumerate(quotation["items"], start=1):
        table_data.append(
            [
                str(index),
                Paragraph(str(item["description"]), small),
                f"{item['quantity']} {item['unit']}",
                f"₹{item['price']:.2f}",
                f"₹{item['total']:.2f}",
            ]
        )

    item_table = Table(
        table_data,
        colWidths=[10 * mm, 78 * mm, 25 * mm, 30 * mm, 32 * mm],
        repeatRows=1,
    )

    item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243d4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c5c5c5")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(item_table)
    story.append(Spacer(1, 5 * mm))

    totals = [
        ["SUB TOTAL:", f"₹{quotation['subtotal']:.2f}"],
        ["SGST:", f"₹{quotation['sgst']:.2f}"],
        ["CGST:", f"₹{quotation['cgst']:.2f}"],
        ["GRAND TOTAL:", f"₹{quotation['grand_total']:.2f}"],
    ]

    totals_table = Table(
        totals,
        colWidths=[40 * mm, 35 * mm],
        hAlign="RIGHT",
    )
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LINEABOVE", (0, 3), (-1, 3), 1, colors.HexColor("#243d4a")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(totals_table)

    story.append(Spacer(1, 15 * mm))
    story.append(
        Paragraph(
            "We hope you find our offer to be in line with your requirement.",
            normal,
        )
    )

    story.append(Spacer(1, 15 * mm))

    signature_data = [
        [
            "",
            Paragraph(
                f"<b>For, {company.get('company_name', 'INTERIOR PROJECTS')}</b>"
                "<br/><br/><br/>"
                "<b>Authorized Signatory</b>",
                ParagraphStyle(
                    "Signature",
                    parent=normal,
                    alignment=2,
                ),
            ),
        ]
    ]

    signature_table = Table(
        signature_data,
        colWidths=[105 * mm, 70 * mm],
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(signature_table)

    story.append(Spacer(1, 18 * mm))
    story.append(
        Paragraph(
            "<b>TERMS AND CONDITIONS:</b>",
            normal,
        )
    )
    story.append(Spacer(1, 2 * mm))

    terms = quotation.get("terms_conditions") or ""
    terms_html = "<br/>".join(
        f"{i + 1}. {line.strip()}"
        for i, line in enumerate(terms.splitlines())
        if line.strip()
    )

    story.append(Paragraph(terms_html, small))

    doc.build(story)

    return path
