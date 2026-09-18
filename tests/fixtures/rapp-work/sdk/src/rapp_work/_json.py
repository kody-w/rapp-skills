from __future__ import annotations

import json


def strict_json_loads(raw, *, where):
    return json.loads(raw)


def canonical_text(value):
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
