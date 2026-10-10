---
name: hello
description: Greet someone by name. Use when the user asks to be greeted or to try a one-file skill that also carries its own agent.
license: MIT
metadata:
  format: rapp-agent-md/1
  spec: https://raw.githubusercontent.com/kody-w/rapp-skills/main/AGENT-MD.md
  agent-class: HelloAgent
  code-sha256: 25714ca5af848681974552629c537e9473d2444bbff54e837e336146ced35904
  signed-by: example-unsigned
---
# Hello

Greet the person by name. If no name is given, ask for one first.

You can do this yourself: say "Hello, <name>!". If your tool can run checked agents, use the agent below instead.

## Examples
- who: Ada -> Hello, Ada!
- who: (none) -> Hello, friend!

## Agent
This block is text until a host checks it (see the spec) and decides to run it.

```python
from agents.basic_agent import BasicAgent


class HelloAgent(BasicAgent):
    """Greets a person by name. Same input, same output."""

    def __init__(self):
        self.name = "Hello"
        self.metadata = {"name": self.name, "description": "Greets a person by name.",
                         "parameters": {"type": "object", "properties": {"who": {"type": "string"}}, "required": ["who"]}}
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        return f"Hello, {kwargs.get('who', 'friend')}!"
```
