# build llm context from retrieved documents


def build_context(documents):

    context = []

    sources = []

    for document in documents:

        context.append(
            document["text"]
        )

        metadata = document["metadata"]

        source = ""

        if metadata["source"] == "youtube":

            source = (
                f"🎥 {metadata.get('title','Unknown')}"
            )

            if "timestamp" in metadata:

                source += (
                    f" ({metadata['timestamp']})"
                )

        elif metadata["source"] == "pdf":

            source = (
                f"📄 {metadata.get('file','PDF')}"
            )

            if "page" in metadata:

                source += (
                    f" (Page {metadata['page']})"
                )

        elif metadata["source"] == "website":

            source = (
                f"🌐 {metadata.get('url','Website')}"
            )

        elif metadata["source"] == "text":

            source = "📝 User Notes"

        if source not in sources:

            sources.append(source)

    return {

        "context":"\n\n".join(context),

        "sources":sources

    }