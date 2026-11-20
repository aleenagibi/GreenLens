from app.services.context_window_service import ContextWindowService


def test_context_window_keeps_recent_messages_in_order():
    history = [
        {"role": "user", "content": "old context " * 300},
        {"role": "assistant", "content": "old answer " * 300},
        {"role": "user", "content": "recent question"},
        {"role": "assistant", "content": "recent answer"},
    ]

    messages, metadata = ContextWindowService.prepare(
        prompt="continue", history=history, context_length=2048, max_output_tokens=512
    )

    assert messages[-1] == {"role": "user", "content": "continue"}
    assert messages[:-1] == history[-2:]
    assert metadata["history_messages_dropped"] == 2
    assert metadata["context_trimmed"] is True


def test_missing_model_context_uses_conservative_fallback():
    messages, metadata = ContextWindowService.prepare(
        prompt="hello", history=[], context_length=None, max_output_tokens=512
    )

    assert messages == [{"role": "user", "content": "hello"}]
    assert metadata["context_window_tokens"] == 8192
    assert metadata["context_metadata_available"] is False


def test_current_prompt_is_never_silently_removed():
    try:
        ContextWindowService.prepare(
            prompt="x" * 100_000, history=[], context_length=2048, max_output_tokens=512
        )
    except ValueError as exc:
        assert "shorten the prompt" in str(exc)
    else:
        raise AssertionError("Oversized current prompt should be rejected")
