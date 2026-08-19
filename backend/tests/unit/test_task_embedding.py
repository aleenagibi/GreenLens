from app.engines.task_embedding_engine import TaskEmbeddingEngine


def test_task_embedding():
    engine = TaskEmbeddingEngine()

    embedding = engine.generate_embedding(
        "Write a Python program to sort a list."
    )

    assert len(embedding) == 384