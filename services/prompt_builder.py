import fitz


def extract_pdf_text(pdf_file):

    document = fitz.open(stream=pdf_file.read(), filetype="pdf")

    full_text = ""

    for page in document:

        full_text += page.get_text()

        full_text += "\n"

    document.close()

    return full_text