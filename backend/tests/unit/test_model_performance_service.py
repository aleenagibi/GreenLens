from app.services.model_performance_service import (
    ModelPerformanceService,
)


def setup_function():
    ModelPerformanceService.clear()


def test_record_latency():

    ModelPerformanceService.record_latency(
        "test-model",
        1000.0,
    )

    latency = (
        ModelPerformanceService.get_latency(
            "test-model"
        )
    )

    assert latency == 1000.0


def test_average_latency():

    ModelPerformanceService.record_latency(
        "test-model",
        1000.0,
    )

    ModelPerformanceService.record_latency(
        "test-model",
        2000.0,
    )

    latency = (
        ModelPerformanceService.get_latency(
            "test-model"
        )
    )

    assert latency == 1500.0


def test_sample_count():

    ModelPerformanceService.record_latency(
        "test-model",
        1000.0,
    )

    ModelPerformanceService.record_latency(
        "test-model",
        2000.0,
    )

    record = (
        ModelPerformanceService.get_record(
            "test-model"
        )
    )

    assert record is not None
    assert record.sample_count == 2


def test_unknown_model():

    latency = (
        ModelPerformanceService.get_latency(
            "unknown-model"
        )
    )

    assert latency is None