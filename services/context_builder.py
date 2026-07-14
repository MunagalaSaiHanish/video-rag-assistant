# Build structured context for the LLM


def build_context(documents):

    context_sections = []

    sources = []

    for document in documents:

        metadata = document.get(
            "metadata",
            {}
        )

        source_type = metadata.get(
            "source",
            "unknown"
        )

        if source_type == "youtube":

            title = metadata.get(
                "title",
                "YouTube Video"
            )

            citation = (
                f"Timestamp: "
                f"{document.get('start', 0)}s"
            )

        elif source_type == "pdf":

            title = metadata.get(
                "file",
                "PDF Document"
            )

            citation = (
                f"Page: "
                f"{metadata.get('page', 'Unknown')}"
            )

        elif source_type == "website":

            title = metadata.get(
                "url",
                "Website"
            )

            citation = "Website"

        elif source_type == "notes":

            title = metadata.get(
                "title",
                "Notes"
            )

            citation = "Notes"

        else:

            title = "Document"

            citation = ""

        section = f"""
========================
SOURCE   : {source_type.upper()}
TITLE    : {title}
{citation}
========================

{document["text"]}
"""

        context_sections.append(
            section
        )

        if title not in sources:

            sources.append(
                title
            )

    return {

        "context": "\n\n".join(
            context_sections
        ),

        "sources": sources

    }