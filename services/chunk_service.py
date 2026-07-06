from langchain_text_splitters import RecursiveCharacterTextSplitter


#chunk plain text

def chunk_text(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_text(text)

    return chunks


#chunk transcript while preserving timestamps

def chunk_transcript(transcript_segments):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    current_text = ""
    current_start = None
    current_end = None

    for segment in transcript_segments:

        if current_start is None:
            current_start = segment["start"]

        current_text += segment["text"] + " "
        current_end = segment["end"]

        if len(current_text) >= 1000:

            split_chunks = text_splitter.split_text(current_text)

            for chunk in split_chunks:

                chunks.append(
                    {
                        "text": chunk,
                        "start": current_start,
                        "end": current_end
                    }
                )

            current_text = ""
            current_start = None
            current_end = None

    if current_text:

        split_chunks = text_splitter.split_text(current_text)

        for chunk in split_chunks:

            chunks.append(
                {
                    "text": chunk,
                    "start": current_start,
                    "end": current_end
                }
            )

    return chunks

# chunk document objects while preserving metadata

def chunk_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for document in documents:

        split_chunks = text_splitter.split_text(
            document["text"]
        )

        for chunk in split_chunks:

            chunks.append(
                {
                    "text": chunk,
                    "metadata": document["metadata"]
                }
            )

    return chunks