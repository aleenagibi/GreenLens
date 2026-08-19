from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Standard user request.
    GreenLens chooses the provider automatically.
    """

    prompt: str = Field(
        ...,
        min_length=1,
        description="User prompt",
        examples=["Explain Artificial Intelligence"],
    )


class AdvancedChatRequest(BaseModel):
    """
    Developer request.
    Allows manual model selection.
    """

    prompt: str = Field(..., min_length=1)

    model: str | None = None

    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
    )

    max_tokens: int = Field(
        default=512,
        gt=0,
    )


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class RecommendationInfo(BaseModel):
    task_type: str
    score: float
    reason: str


class BenchmarkInfo(BaseModel):
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    provider: str
    model: str
    success: bool


class SustainabilityInfo(BaseModel):
    energy_wh: float
    carbon_g: float
    green_score: float


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: TokenUsage
    recommendation: RecommendationInfo
    benchmark: BenchmarkInfo
    sustainability: SustainabilityInfo
    pipeline: dict