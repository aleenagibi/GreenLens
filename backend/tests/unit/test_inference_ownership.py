from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import InferenceRecord, User


def _record(user_id, carbon_g):
    return InferenceRecord(
        user_id=user_id,
        prompt="test prompt",
        provider="openrouter",
        model="test/model",
        task_type="general",
        recommendation_score=5.0,
        latency_ms=100.0,
        prompt_tokens=2,
        completion_tokens=3,
        total_tokens=5,
        energy_wh=0.1,
        carbon_g=carbon_g,
        green_score=5.0,
        success=True,
    )


def test_inference_records_are_isolated_by_user():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        user_a = User(email="user-a@example.test")
        user_b = User(email="user-b@example.test")
        db.add_all([user_a, user_b])
        db.flush()

        db.add_all([
            _record(user_a.id, 0.1),
            _record(user_a.id, 0.2),
            _record(user_b.id, 0.9),
        ])
        db.commit()

        user_a_count = (
            db.query(func.count(InferenceRecord.id))
            .filter(InferenceRecord.user_id == user_a.id)
            .scalar()
        )
        user_b_count = (
            db.query(func.count(InferenceRecord.id))
            .filter(InferenceRecord.user_id == user_b.id)
            .scalar()
        )
        user_a_carbon = (
            db.query(func.sum(InferenceRecord.carbon_g))
            .filter(InferenceRecord.user_id == user_a.id)
            .scalar()
        )
        user_b_carbon = (
            db.query(func.sum(InferenceRecord.carbon_g))
            .filter(InferenceRecord.user_id == user_b.id)
            .scalar()
        )

        assert user_a_count == 2
        assert user_b_count == 1
        assert abs(user_a_carbon - 0.3) < 1e-9
        assert abs(user_b_carbon - 0.9) < 1e-9

    engine.dispose()
