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
    }

    result = ModelCatalogService.normalize_model(
        raw_model
    )

    assert result["model_id"] == "test/model:free"
    assert result["display_name"] == "Test Model"
    assert result["is_free"] is True
    assert result["prompt_price"] == 0
    assert result["completion_price"] == 0


def test_normalize_paid_model():

    raw_model = {
        "id": "test/model",
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

    assert result["is_free"] is False
    assert result["prompt_price"] == 0.000001


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
    assert result[0]["id"] == "test/model:free"