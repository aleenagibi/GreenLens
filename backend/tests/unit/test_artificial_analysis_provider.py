from unittest.mock import Mock, patch

from app.benchmarks.artificial_analysis_provider import (
    ArtificialAnalysisProvider,
)


def test_normalize_model_id():

    result = (
        ArtificialAnalysisProvider
        .normalize_model_id(
            "openai/gpt-oss-20b:free"
        )
    )

    assert result == "gpt-oss-20b"


def test_normalize_model_without_free_suffix():

    result = (
        ArtificialAnalysisProvider
        .normalize_model_id(
            "z-ai/glm-5.2:free"
        )
    )

    assert result == "glm-5.2"


def test_find_model_by_slug():

    models = [
        {
            "slug": "gpt-oss-20b",
            "name": "gpt-oss-20B",
        }
    ]

    result = (
        ArtificialAnalysisProvider.find_model(
            models,
            "gpt-oss-20b",
        )
    )

    assert result is not None
    assert result["slug"] == "gpt-oss-20b"


def test_find_model_returns_none():

    models = [
        {
            "slug": "gpt-oss-20b",
        }
    ]

    result = (
        ArtificialAnalysisProvider.find_model(
            models,
            "unknown-model",
        )
    )

    assert result is None


@patch(
    "app.benchmarks.artificial_analysis_provider.requests.get"
)
def test_fetch_models(mock_get):

    response = Mock()

    response.json.return_value = {
        "tier": "free",
        "pagination": {
            "page": 1,
            "page_size": 200,
            "total_pages": 1,
            "has_more": False,
        },
        "data": [
            {
                "slug": "gpt-oss-20b",
                "evaluations": {
                    "artificial_analysis_intelligence_index": 24.5,
                    "artificial_analysis_coding_index": 18.5,
                    "artificial_analysis_agentic_index": 27.6,
                },
            }
        ],
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    provider = ArtificialAnalysisProvider(
        api_key="test-key"
    )

    models = provider.fetch_models()

    assert len(models) == 1

    assert models[0]["slug"] == (
        "gpt-oss-20b"
    )

    mock_get.assert_called_once_with(
        provider.FREE_MODELS_ENDPOINT,
        headers={
            "x-api-key": "test-key"
        },
        params={
            "page": 1
        },
        timeout=15,
    )


@patch(
    "app.benchmarks.artificial_analysis_provider.requests.get"
)
def test_get_general_benchmark(mock_get):

    response = Mock()

    response.json.return_value = {
        "tier": "free",
        "pagination": {
            "page": 1,
            "page_size": 200,
            "total_pages": 1,
            "has_more": False,
        },
        "data": [
            {
                "slug": "gpt-oss-20b",
                "evaluations": {
                    "artificial_analysis_intelligence_index": 24.5,
                    "artificial_analysis_coding_index": 18.5,
                    "artificial_analysis_agentic_index": 27.6,
                },
            }
        ],
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    provider = ArtificialAnalysisProvider(
        api_key="test-key"
    )

    result = provider.get_benchmark(
        "openai/gpt-oss-20b:free",
        "general",
    )

    assert result is not None
    assert result.model == (
        "openai/gpt-oss-20b:free"
    )
    assert result.task_type == "general"

    assert result.benchmark == (
        "Artificial Analysis Intelligence Index"
    )

    assert result.score == 2.45

    assert result.source == (
        "ArtificialAnalysis"
    )

    assert result.verified is True


@patch(
    "app.benchmarks.artificial_analysis_provider.requests.get"
)
def test_get_coding_benchmark(mock_get):

    response = Mock()

    response.json.return_value = {
        "pagination": {
            "has_more": False,
        },
        "data": [
            {
                "slug": "gpt-oss-20b",
                "evaluations": {
                    "artificial_analysis_intelligence_index": 24.5,
                    "artificial_analysis_coding_index": 18.5,
                    "artificial_analysis_agentic_index": 27.6,
                },
            }
        ],
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    provider = ArtificialAnalysisProvider(
        api_key="test-key"
    )

    result = provider.get_benchmark(
        "openai/gpt-oss-20b:free",
        "coding",
    )

    assert result is not None

    assert result.benchmark == (
        "Artificial Analysis Coding Index"
    )

    assert result.score == 1.85


def test_missing_api_key():

    provider = ArtificialAnalysisProvider(
        api_key=None
    )

    result = provider.get_benchmark(
        "openai/gpt-oss-20b:free",
        "general",
    )

    assert result is None


@patch(
    "app.benchmarks.artificial_analysis_provider.requests.get"
)
def test_unknown_model(mock_get):

    response = Mock()

    response.json.return_value = {
        "pagination": {
            "has_more": False,
        },
        "data": [],
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    provider = ArtificialAnalysisProvider(
        api_key="test-key"
    )

    result = provider.get_benchmark(
        "unknown/model",
        "general",
    )

    assert result is None