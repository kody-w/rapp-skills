"""Two agents in one file, the way a server serves them: every public class with perform is a tool."""

from agents.basic_agent import BasicAgent


class GreetAgent(BasicAgent):
    def __init__(self):
        self.name = "GreetAgent"
        self.metadata = {
            "name": self.name,
            "description": "Says hello.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Name to greet"}},
                "required": [],
            },
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs) -> str:
        return f"Hello, {kwargs.get('name', 'World')}!"


class FarewellAgent(BasicAgent):
    def __init__(self):
        self.name = "FarewellAgent"
        self.metadata = {
            "name": self.name,
            "description": "Says goodbye.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to see off"},
                    "until": {"type": "string", "description": "When you will meet again"},
                },
                "required": [],
            },
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs) -> str:
        until = kwargs.get("until")
        return f"Goodbye, {kwargs.get('name', 'World')}!" + (f" See you {until}." if until else "")


class _DraftAgent(BasicAgent):
    """Private by name: a server never serves it, so neither does a skill."""

    def __init__(self):
        self.name = "DraftAgent"
        self.metadata = {"name": self.name, "description": "Not ready.", "parameters": {"type": "object", "properties": {}, "required": []}}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs) -> str:
        return "draft"
