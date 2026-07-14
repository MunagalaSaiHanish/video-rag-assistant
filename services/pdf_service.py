import fitz


def extract_pdf_text(pdf_file):

    try:

        document = fitz.open(

            stream=pdf_file.read(),

            filetype="pdf"

        )

    except Exception:

        return ""

    full_text = ""

    page_count = document.page_count

    for page_number in range(page_count):

        page = document.load_page(
            page_number
        )

        text = page.get_text().strip()

        if not text:

            continue

        full_text += text

        full_text += "\n\n"

    document.close()

    return full_text.strip()