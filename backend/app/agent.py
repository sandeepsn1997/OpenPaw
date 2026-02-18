from datetime import datetime, timezone


class SimpleAgent:
    """A minimal tool-using agent you can later swap with an LLM backend."""

    def run(self, user_message: str) -> tuple[str, str | None]:
        normalized = user_message.lower().strip()

        if "time" in normalized or "date" in normalized:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return f"Current server time is {now}.", "clock"

        if normalized.startswith("echo "):
            return user_message[5:], "echo"

        return (
            "I am your OpenPaw starter agent. Try asking for the current time or prefix with 'echo '.",
            None,
        )
