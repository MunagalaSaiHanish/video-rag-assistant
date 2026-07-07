from services.pdf_service import extract_pdf_text
from services.models.document import Document


def load_pdf(uploaded_file):

    text = extract_pdf_text(
        uploaded_file
    )

    if not text:

        return None

    document = Document.create(

        source="pdf",

        title=uploaded_file.name,

        content=text,

        metadata={

            "file": uploaded_file.name

        }

    )

    return document