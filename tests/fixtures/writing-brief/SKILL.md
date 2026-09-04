---
name: "writing-brief"
description: "Turn a rough idea into a one-page writing brief: audience, promise, outline, tone, and the first sentence. Use when someone has a topic but no structure yet."
license: "MIT"
metadata:
  rapp-skills: "1.0.0"
  source: "playbook"
---

# Writing Brief

Turn a rough idea into a one-page brief the writer can start from.

## Parameters

```json
{
  "type": "object",
  "properties": {
    "topic": {"type": "string", "description": "The idea in the user's words"},
    "audience": {"type": "string", "description": "Who will read it"}
  },
  "required": ["topic"]
}
```

## Steps

1. Restate the topic in one sentence the audience would recognize.
2. Name the single promise the piece makes to that audience.
3. Write a five-part outline, one line each.
4. Choose a tone in three words.
5. Write the first sentence.

Keep the whole brief under 200 words.
