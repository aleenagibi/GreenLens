from pydantic import BaseModel


class ProviderCreate(BaseModel):
    name: str
    model: str
    cost_per_1m_tokens: float
    carbon_score: float
    active: bool = True