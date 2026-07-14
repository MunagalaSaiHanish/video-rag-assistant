from sentence_transformers import SentenceTransformer

# Global model instance
_model = None


def get_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


# Backward compatibility
model = get_model()


def generate_embeddings(chunks):

    if not chunks:
        return []

    return model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )


def generate_document_embeddings(chunks):

    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    vector_records = []

    for chunk, embedding in zip(chunks, embeddings):

        vector_records.append(
            {
                "text": chunk["text"],
                "embedding": embedding,
                "metadata": chunk["metadata"]
            }
        )

    return vector_records