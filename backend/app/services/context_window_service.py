
"""Model-aware conversation context packing for chat inference.

Token counts are conservative estimates. Provider-reported usage remains the
source of truth for actual prompt-token consumption.
"""

from __future__ import annotations

import math
from typing import Any


class ContextWindowService:
    DEFAULT_CONTEXT_LENGTH = 8192
    SAFETY_MARGIN_RATIO = 0.05
    MIN_SAFETY_MARGIN = 256

    # Central instructions applied to every GreenLens conversation.
    SYSTEM_PROMPT = """
You are GreenLens, a professional, helpful, and knowledgeable AI assistant.

Your purpose is to provide accurate, clear, natural, and useful responses.

RESPONSE GUIDELINES:

1. Answer the user's actual question directly.
2. Always produce natural, user-facing responses.
3. Never reveal internal reasoning, private deliberations,
   hidden analysis, or internal response-planning steps.
4. Never generate internal planning headings such as:
   - Understand the User's Goal
   - Analyze the User's Input
   - Determine the Response Strategy
   - Drafting the Content
   - Final Polish
5. Do not narrate how you construct your answers.
6. Do not generate unnecessary numbered analysis stages.
7. Use headings, bullet points, tables, and examples only
   when they genuinely improve readability.
8. Maintain relevant context from previous conversation messages.
9. If the user makes a statement without asking a question,
   acknowledge it naturally instead of inventing a task.
10. Do not invent facts about the user's project or technology.
11. For technical questions, provide accurate and practical
    explanations with relevant examples when appropriate.
12. Clearly communicate uncertainty when information is unavailable.
13. Avoid repetitive introductions and unnecessary conclusions.
14. Adapt the response length to the complexity of the question.

IMPORTANT:
Return only the final answer intended for the user.
Never expose internal analysis or response-planning content.
"""

    @staticmethod
    def estimate_message_tokens(message: dict[str, str]) -> int:
        """Estimate message tokens conservatively."""
        content = message.get("content", "")
        return max(
            1,
            math.ceil(len(content.encode("utf-8")) / 3.5)
        ) + 4

    @classmethod
    def prepare(
        cls,
        *,
        prompt: str,
        history: list[dict[str, str]] | None,
        context_length: int | None,
        max_output_tokens: int,
    ) -> tuple[list[dict[str, str]], dict[str, Any]]:

        # Use catalogue context length when available.
        known = isinstance(context_length, int) and context_length > 0
        window = context_length if known else cls.DEFAULT_CONTEXT_LENGTH

        # Reserve output tokens and a safety margin.
        safety = max(
            cls.MIN_SAFETY_MARGIN,
            math.ceil(window * cls.SAFETY_MARGIN_RATIO)
        )

        input_budget = max(
            1,
            window - max_output_tokens - safety
        )

        # System instruction is always included.
        system_message = {
            "role": "system",
            "content": cls.SYSTEM_PROMPT.strip(),
        }

        current = {
            "role": "user",
            "content": prompt,
        }

        system_tokens = cls.estimate_message_tokens(system_message)
        current_tokens = cls.estimate_message_tokens(current)

        # Ensure the mandatory messages fit.
        mandatory_tokens = system_tokens + current_tokens

        if mandatory_tokens > input_budget:
            raise ValueError(
                "The system instructions and current prompt exceed "
                "the available context budget. Please shorten the prompt "
                "or increase the available context window."
            )

        # Accept only user and assistant messages from conversation history.
        valid_history = [
            {
                "role": item["role"],
                "content": item["content"],
            }
            for item in (history or [])
            if (
                item.get("role") in {"user", "assistant"}
                and isinstance(item.get("content"), str)
                and item["content"].strip()
            )
        ]

        # Group each user message with its corresponding assistant answer.
        turns: list[list[dict[str, str]]] = []

        index = 0

        while index < len(valid_history):
            if (
                index + 1 < len(valid_history)
                and valid_history[index]["role"] == "user"
                and valid_history[index + 1]["role"] == "assistant"
            ):
                turns.append(valid_history[index:index + 2])
                index += 2
            else:
                turns.append([valid_history[index]])
                index += 1

        # Retain the newest complete turns that fit the context budget.
        selected_turns_reversed: list[list[dict[str, str]]] = []

        used = mandatory_tokens

        for turn in reversed(turns):
            cost = sum(
                cls.estimate_message_tokens(message)
                for message in turn
            )

            if used + cost > input_budget:
                # Preserve a contiguous sliding window of recent turns.
                break

            selected_turns_reversed.append(turn)
            used += cost

        # Restore chronological order.
        selected_history = [
            message
            for turn in reversed(selected_turns_reversed)
            for message in turn
        ]

        dropped = len(valid_history) - len(selected_history)

        # Final message sequence sent to the LLM.
        messages = [
            system_message,
            *selected_history,
            current,
        ]

        metadata = {
            "context_window_tokens": window,
            "context_budget_tokens": input_budget,
            "input_tokens_estimated": used,
            "input_tokens_actual": None,
            "history_messages_received": len(valid_history),
            "history_messages_included": len(selected_history),
            "history_messages_dropped": dropped,
            "context_trimmed": dropped > 0,
            "context_metadata_available": known,
        }

        return messages, metadata
