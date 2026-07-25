from app.db.database import Base
from sqlalchemy import Boolean, Column, Float, Integer, String


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    model = Column(String, nullable=False)

    cost_per_1m_tokens = Column(Float, nullable=False)

    carbon_score = Column(Float, nullable=False)

    active = Column(Boolean, default=True)