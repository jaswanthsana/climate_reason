"""
Async wrapper around the OpenAI-compatible K2 Think V2 API.

K2 quirks handled here:
  - reasoning_effort is passed via extra_body (not a standard OpenAI param)
  - The model sometimes wraps JSON output in ```json ... ``` markdown fences
  - We strip those fences before JSON-parsing
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal

from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

ReasoningEffort = Literal["low", "medium", "high"]


def _strip_thinking(text: str) -> str:
    """If the model includes inline chain-of-thought before </think>, extract only what follows."""
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    return text


def _strip_json_fence(text: str) -> str:
    """Remove optional ```json ... ``` or ``` ... ``` wrappers."""
    text = text.strip()
    # Match ```json\n...\n``` or ```\n...\n```
    match = re.match(r"^```(?:json)?\s*\n?([\s\S]*?)\n?```$", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _extract_json_from_text(text: str) -> str:
    """
    Fallback: scan the text and return the largest complete JSON object found.
    Tries each '{' position from left to right and returns the outermost valid JSON.
    Used when the model embeds JSON in prose/thinking without </think>.
    """
    best = ""
    i = 0
    while i < len(text):
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[i:j + 1]
                    if len(candidate) > len(best):
                        best = candidate
                    break
        i += 1
    return best if best else text


class K2Client:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.k2_api_key,
            base_url=settings.k2_api_base_url,
        )
        self.model = settings.k2_model_name

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        reasoning_effort: ReasoningEffort = "medium",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> tuple[str, str]:
        """
        Call K2 and return (content_text, reasoning_text).
        reasoning_text may be empty if the model doesn't expose its chain-of-thought.
        """
        logger.info("K2 call | effort=%s | prompt_len=%d", reasoning_effort, len(user_prompt))

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        raw_content = choice.message.content or ""

        # Extract the actual response after the inline thinking block
        content = _strip_thinking(raw_content)

        # Some K2 versions expose reasoning in a separate field; else use the stripped thinking block
        reasoning: str = ""
        if hasattr(choice.message, "reasoning_content") and choice.message.reasoning_content:
            reasoning = choice.message.reasoning_content
        elif hasattr(choice.message, "reasoning") and choice.message.reasoning:
            reasoning = choice.message.reasoning
        elif "</think>" in raw_content:
            reasoning = raw_content.split("</think>", 1)[0].strip()

        logger.info("K2 response | tokens=%s | has_reasoning=%s",
                    response.usage.total_tokens if response.usage else "?",
                    bool(reasoning))
        return content, reasoning

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        reasoning_effort: ReasoningEffort = "medium",
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> tuple[dict[str, Any], str]:
        """
        Like complete(), but parses the response as JSON.
        Returns (parsed_dict, reasoning_text).
        Raises ValueError if JSON parsing fails.
        """
        content, reasoning = await self.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        clean = _strip_json_fence(content)
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            # Fallback: model may have embedded JSON in thinking text without </think>
            extracted = _extract_json_from_text(content)
            try:
                parsed = json.loads(extracted)
                logger.warning("JSON extracted from thinking text (fallback)")
            except json.JSONDecodeError as exc:
                logger.error("JSON parse failed. Raw content:\n%s", content[:500])
                raise ValueError(f"K2 returned non-JSON output: {exc}") from exc
        return parsed, reasoning


# Singleton — import and use this across the app
k2 = K2Client()
