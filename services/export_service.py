from io import BytesIO
from datetime import datetime
import re
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    HRFlowable
)

LOGO_PATH = "assets/pdf lumina logo.png"


def clean_markdown(text: str):

    if not text:

        return ""

    text = re.sub(
        r"^#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )

    text = text.replace("---", "")
    text = text.replace("___", "")
    text = text.replace("`", "")
    text = text.replace("\r", "")

    return text.strip()


def draw_footer(canvas, doc):

    canvas.saveState()

    y = 25

    canvas.setFont(
        "Helvetica",
        9
    )

    canvas.drawString(
        40,
        y,
        "Powered by"
    )

    if os.path.exists(LOGO_PATH):

        try:

            canvas.drawImage(
                LOGO_PATH,
                90,
                y - 8,
                width=90,
                height=24,
                mask="auto"
            )

        except Exception:

            canvas.drawString(
                90,
                y,
                "Lumina AI"
            )

    else:

        canvas.drawString(
            90,
            y,
            "Lumina AI"
        )

    canvas.drawRightString(

        doc.pagesize[0] - 40,

        y,

        f"Page {canvas.getPageNumber()}"

    )

    canvas.restoreState()


def generate_pdf(

    metadata,

    topic,

    summary,

    takeaways,

    topics

):

    metadata = metadata or {}

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        leftMargin=45,

        rightMargin=45,

        topMargin=45,

        bottomMargin=60

    )

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = colors.HexColor("#5B4CF0")

    heading_style = styles["Heading2"]
    heading_style.textColor = colors.HexColor("#5B4CF0")

    normal_style = styles["BodyText"]

    story = []

    story.append(

        Paragraph(

            clean_markdown(topic),

            title_style

        )

    )

    story.append(
        Spacer(
            1,
            0.25 * inch
        )
    )

    story.append(
        Paragraph(
            f"<b>Title:</b> {metadata.get('title','Knowledge Report')}",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Source:</b> {metadata.get('source','YouTube')}",
            normal_style
        )
    )

    if metadata.get("channel"):

        story.append(

            Paragraph(

                f"<b>Channel:</b> {metadata.get('channel')}",

                normal_style

            )

        )

    if metadata.get("url"):

        url = metadata["url"]

        story.append(

            Paragraph(

                f"<b>URL:</b> <link href='{url}' color='blue'>{url}</link>",

                normal_style

            )

        )

    story.append(

        Paragraph(

            f"<b>Generated On:</b> {datetime.now().strftime('%d %b %Y %I:%M %p')}",

            normal_style

        )

    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey
        )
    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        Paragraph(
            "Executive Summary",
            heading_style
        )
    )

    story.append(

        Paragraph(

            clean_markdown(summary).replace(
                "\n",
                "<br/>"
            ),

            normal_style

        )

    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey
        )
    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        Paragraph(
            "Key Takeaways",
            heading_style
        )
    )

    takeaway_items = [

        ListItem(

            Paragraph(

                clean_markdown(item),

                normal_style

            )

        )

        for item in takeaways

    ]

    story.append(

        ListFlowable(

            takeaway_items,

            bulletType="bullet"

        )

    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey
        )
    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        Paragraph(
            "Main Topics",
            heading_style
        )
    )

    topic_items = [

        ListItem(

            Paragraph(

                clean_markdown(item),

                normal_style

            )

        )

        for item in topics

    ]

    story.append(

        ListFlowable(

            topic_items,

            bulletType="bullet"

        )

    )

    doc.build(

        story,

        onFirstPage=draw_footer,

        onLaterPages=draw_footer

    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf