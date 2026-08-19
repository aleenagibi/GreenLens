"""
Task Embedding Engine

Converts a user prompt into a semantic vector representation.
"""

from sentence_transformers import SentenceTransformer


class TaskEmbeddingEngine:
    """
    Generates semantic embeddings for user tasks.
    """

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def generate_embedding(self, prompt: str) -> list[float]:
        """
        Generate an embedding for a user prompt.
        """

        embedding = self.model.encode(
            prompt,
            convert_to_numpy=True,
        )

        return embedding.tolist()