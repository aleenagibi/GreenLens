from app.models.model_registry import ModelRegistry


def setup_models():

    ModelRegistry.load_models(
        [
            {
                "model_id": "openai/gpt-oss-20b:free",
                "display_name": "GPT-OSS 20B",
                "is_free": True,
            },
            {
                "model_id": "example/paid-model",
                "display_name": "Paid Model",
                "is_free": False,
            },
        ]
    )


def test_load_models():

    setup_models()

    models = ModelRegistry.get_all()

    assert len(models) == 2


def test_get_free_models():

    setup_models()

    models = ModelRegistry.get_free_models()

    assert len(models) == 1
    assert models[0].is_free is True


def test_get_paid_models():

    setup_models()

    models = ModelRegistry.get_paid_models()

    assert len(models) == 1
    assert models[0].is_free is False


def test_get_by_id():

    setup_models()

    model = ModelRegistry.get_by_id(
        "openai/gpt-oss-20b:free"
    )

    assert model is not None
    assert model.display_name == "GPT-OSS 20B"