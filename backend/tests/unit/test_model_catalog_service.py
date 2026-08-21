from unittest.mock import Mock, patch

from app.services.model_catalog_service import (
    ModelCatalogService,
)


def test_normalize_free_model():

    raw_model = {
        "id": "test/model:free",
        "name": "Test Model",
        "context_length": 8192,
        "pricing": {
            "prompt": "0",
            "completion": "0",
        },
        "architecture": {
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        "supported_parameters": [
            "temperature",
            "stream",
        ],
    }

    result = ModelCatalogService.normalize_model(
        raw_model
    )

    assert result["model_id"] == (
        "test/model:free"
    )

    assert result["display_name"] == (
        "Test Model"
    )

    assert result["provider"] == "test"

    assert result["context_length"] == 8192

    assert result["is_free"] is True

    assert result["prompt_price"] == 0.0

    assert result["completion_price"] == 0.0

    assert result["input_modalities"] == [
        "text"
    ]

    assert result["output_modalities"] == [
        "text"
    ]

    assert result["supported_parameters"] == [
        "temperature",
        "stream",
    ]


def test_normalize_paid_model():

    raw_model = {
        "id": "openai/test-model",
        "name": "Paid Model",
        "context_length": 8192,
        "pricing": {
            "prompt": "0.000001",
            "completion": "0.000002",
        },
        "architecture": {
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
    }

    result = ModelCatalogService.normalize_model(
        raw_model
    )

    assert result["model_id"] == (
        "openai/test-model"
    )

    assert result["provider"] == "openai"

    assert result["is_free"] is False

    assert result["prompt_price"] == 0.000001

    assert result["completion_price"] == 0.000002


def test_reasoning_model():

    raw_model = {
        "id": "test/reasoning-model",
        "name": "Reasoning Model",
        "pricing": {
            "prompt": "0.000001",
            "completion": "0.000002",
        },
        "architecture": {
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        "supported_parameters": [
            "reasoning",
        ],
    }

    result = ModelCatalogService.normalize_model(
        raw_model
    )

    assert result["supports_reasoning"] is True


def test_non_text_model():

    raw_model = {
        "id": "test/image-model",
        "name": "Image Model",
        "pricing": {
            "prompt": "0",
            "completion": "0",
        },
        "architecture": {
            "input_modalities": ["text"],
            "output_modalities": ["image"],
        },
    }

    result = ModelCatalogService.normalize_model(
        raw_model
    )

    assert result["is_free"] is True

    assert "text" in result["input_modalities"]

    assert "image" in result["output_modalities"]


@patch(
    "app.services.model_catalog_service.requests.get"
)
def test_fetch_models(mock_get):

    mock_response = Mock()

    mock_response.json.return_value = {
        "data": [
            {
                "id": "test/model:free",
                "name": "Test Model",
                "pricing": {
                    "prompt": "0",
                    "completion": "0",
                },
            }
        ]
    }

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = ModelCatalogService.fetch_models()

    assert len(result) == 1

    assert result[0]["id"] == (
        "test/model:free"
    )

    mock_get.assert_called_once_with(
        ModelCatalogService.OPENROUTER_MODELS_URL,
        timeout=15,
    )


def test_get_free_models():

    models = [
        {
            "model_id": "free/model",
            "is_free": True,
        },
        {
            "model_id": "paid/model",
            "is_free": False,
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService.get_free_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "free/model"
    )


def test_get_paid_models():

    models = [
        {
            "model_id": "free/model",
            "is_free": True,
        },
        {
            "model_id": "paid/model",
            "is_free": False,
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService.get_paid_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "paid/model"
    )


def test_get_text_models():

    models = [
        {
            "model_id": "text/model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        {
            "model_id": "image/model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["image"],
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService.get_text_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "text/model"
    )


def test_get_free_text_models():

    models = [
        {
            "model_id": "free/text",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        {
            "model_id": "paid/text",
            "is_free": False,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService.get_free_text_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "free/text"
    )


def test_get_chat_models():

    models = [
        {
            "model_id": "general/text-model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        {
            "model_id": "openrouter/free",
            "is_free": True,
            "input_modalities": [
                "text",
                "image",
            ],
            "output_modalities": ["text"],
        },
        {
            "model_id": "audio/model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["audio"],
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService.get_chat_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "general/text-model"
    )


def test_get_free_chat_models():

    models = [
        {
            "model_id": "free/text-model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        {
            "model_id": "paid/text-model",
            "is_free": False,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService
            .get_free_chat_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "free/text-model"
    )


def test_get_paid_chat_models():

    models = [
        {
            "model_id": "free/text-model",
            "is_free": True,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
        {
            "model_id": "paid/text-model",
            "is_free": False,
            "input_modalities": ["text"],
            "output_modalities": ["text"],
        },
    ]

    with patch.object(
        ModelCatalogService,
        "get_normalized_models",
        return_value=models,
    ):
        result = (
            ModelCatalogService
            .get_paid_chat_models()
        )

    assert len(result) == 1

    assert result[0]["model_id"] == (
        "paid/text-model"
    )