import numpy as np

from services.embedding_service import model


class Retriever:

    def __init__(
        self,
        index,
        vector_records
    ):

        self.index = index
        self.vector_records = vector_records

    def search(
        self,
        question,
        top_k=3
    ):

        question_embedding = model.encode(
            [question]
        )

        question_embedding = np.array(
            question_embedding
        ).astype("float32")

        distances, indices = self.index.search(
            question_embedding,
            top_k
        )

        results = []

        for idx in indices[0]:

            if idx == -1:
                continue

            results.append(
                self.vector_records[idx]
            )

        return results