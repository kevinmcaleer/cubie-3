"""The AI brain: send a camera frame to Claude, get a judgement back.

Primary path is Claude via the GitHub Copilot SDK (uses the Copilot
subscription — no separate API account). Fallback is the Anthropic API
directly. Both return the same ZoneJudgement, so the rest of the robot
doesn't care which one is in use.
"""

import asyncio
import base64
import json
import re
from dataclasses import dataclass

SYSTEM_PROMPT = """You are the AI brain of Cubie-3, a small wheeled robot that inspects
Kevin's robotics workshop. You are judgmental but constructive — like a friend who is
brilliant at organising and slightly disappointed in Kevin. British humour, dry, never mean.

For each photo of a workshop zone, reply with ONLY a JSON object, no other text:
{
  "verdict": "one or two sassy sentences about the state of this zone, spoken aloud by the robot",
  "suggestion": "ONE concrete, achievable tidying action for this zone",
  "score": <integer 1-10, where 10 is perfectly organised>
}

Keep the verdict under 40 words — it goes through text-to-speech.
Base everything only on what is actually visible in the image."""


@dataclass
class ZoneJudgement:
    zone: str
    verdict: str
    suggestion: str
    score: int


def _parse_judgement(text, zone):
    """Pull the JSON object out of the model's reply (it may wrap it in prose or fences)."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model reply: {text[:200]}")
    data = json.loads(match.group(0))
    return ZoneJudgement(
        zone=zone,
        verdict=data["verdict"],
        suggestion=data["suggestion"],
        score=int(data["score"]),
    )


class CopilotJudge:
    """Claude via the GitHub Copilot SDK (pip install github-copilot-sdk).

    Authenticates with the signed-in GitHub user or GH_TOKEN/GITHUB_TOKEN env vars.
    """

    def __init__(self, model="claude-opus-4.8"):
        self.model = model
        self._client = None

    async def start(self):
        from copilot import CopilotClient
        self._client = CopilotClient()
        await self._client.start()

    async def stop(self):
        if self._client:
            await self._client.stop()
            self._client = None

    async def judge_zone(self, jpeg_bytes, zone):
        from copilot.session import PermissionHandler
        from copilot.session_events import AssistantMessageData, SessionIdleData

        reply_parts = []
        done = asyncio.Event()

        def on_event(event):
            match event.data:
                case AssistantMessageData() as data:
                    reply_parts.append(data.content)
                case SessionIdleData():
                    done.set()

        async with await self._client.create_session(
            model=self.model,
            on_permission_request=PermissionHandler.approve_all,
        ) as session:
            session.on(on_event)
            await session.send(
                f"{SYSTEM_PROMPT}\n\nThis photo is the zone called: {zone}",
                attachments=[{
                    "type": "blob",
                    "data": base64.standard_b64encode(jpeg_bytes).decode("utf-8"),
                    "mimeType": "image/jpeg",
                }],
            )
            await done.wait()

        return _parse_judgement("".join(reply_parts), zone)


class AnthropicJudge:
    """Fallback: Claude via the Anthropic API directly (needs ANTHROPIC_API_KEY)."""

    def __init__(self, model="claude-opus-4-8"):
        import anthropic
        self.model = model
        self._client = anthropic.AsyncAnthropic()

    async def start(self):
        pass

    async def stop(self):
        pass

    async def judge_zone(self, jpeg_bytes, zone):
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "verdict": {"type": "string"},
                            "suggestion": {"type": "string"},
                            "score": {"type": "integer"},
                        },
                        "required": ["verdict", "suggestion", "score"],
                        "additionalProperties": False,
                    },
                }
            },
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.standard_b64encode(jpeg_bytes).decode("utf-8"),
                        },
                    },
                    {"type": "text", "text": f"This photo is the zone called: {zone}"},
                ],
            }],
        )
        text = next(b.text for b in response.content if b.type == "text")
        return _parse_judgement(text, zone)


def make_judge(prefer="copilot", model=None):
    """Build a judge, preferring the Copilot SDK and falling back to the Anthropic API."""
    if prefer == "copilot":
        try:
            import copilot  # noqa: F401
            return CopilotJudge(model=model or "claude-opus-4.8")
        except ImportError:
            print("Copilot SDK not installed, falling back to the Anthropic API")
    return AnthropicJudge(model=model or "claude-opus-4-8")
