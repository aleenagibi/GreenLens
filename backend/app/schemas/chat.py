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


class ModelComparisonInfo(BaseModel):
    rank: int
    model: str
    display_name: str | None = None
    provider: str | None = None
    is_free: bool
    fit_score: float
    capability_score: float | None = None
    capability_source: str
    carbon_score: float | None = None
    latency_score: float | None = None
    complexity_score: float | None = None
    estimated_energy_wh: float | None = None
    estimated_carbon_g: float | None = None
    selected: bool = False
    ideal: bool = False


class RoutingInfo(BaseModel):
    ideal_model: str
    ideal_display_name: str | None = None
    ideal_is_free: bool
    selected_model: str
    selected_display_name: str | None = None
    selected_is_free: bool
    capability_gap: float | None = None
    fit_score: float
    used_free_alternative: bool
    reason: str
    summary: str
    comparison: list[ModelComparisonInfo]


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: TokenUsage
    recommendation: RecommendationInfo
    benchmark: BenchmarkInfo
    sustainability: SustainabilityInfo
    pipeline: dict
    routing: RoutingInfo
