from sentence_transformers import SentenceTransformer

# embedding model

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# generate embeddings from plain text chunks

def generate_embeddings(chunks):

    return model.encode(chunks)


# generate embeddings from document chunks

def generate_document_embeddings(chunks):

    texts = []

    for chunk in chunks:

        texts.append(
            chunk["text"]
        )

    embeddings = model.encode(texts)

    vector_records = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        vector_records.append(
            {
                "text": chunk["text"],

                "embedding": embedding,

                "metadata": chunk["metadata"]
            }
        )

    return vector_records