from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from pathlib import Path


def canonical(value):
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def content(operation):
    return canonical(
        {
            "fixture": "canonical-sdk-boundary",
            "operation": operation,
            "version": 2 if operation == "update" else 1,
        }
    ) + b"\n"


def plan_for(operation, inputs):
    target = Path(
        inputs["target"] if operation == "migrate" else inputs["root"]
    )
    managed = target / "install.json"
    after = content(operation)
    replace = operation == "update"
    action = {
        "bytes": len(after),
        "content_base64": base64.b64encode(after).decode("ascii"),
        "expected_sha256": sha(managed.read_bytes()) if replace else None,
        "mode": 0o600,
        "operation": "replace" if replace else "create",
        "path": "install.json",
        "sha256": sha(after),
    }
    return {
        "actions": [action],
        "network": False,
        "operation": operation,
        "schema": "rapp-work-plan-fixture/1",
        "target": str(target),
    }


def envelope(operation, status, result):
    return {
        "operation": operation,
        "profile": "rapp-work-sdk/1",
        "protocol": "rapp-work/1",
        "refusal": None,
        "result": result,
        "schema": "rapp-work-result/1",
        "status": status,
    }


def execute(operation, inputs):
    if operation == "status":
        return envelope(
            operation,
            "ok",
            {"network": False, "status": "available"},
        )
    if operation == "verify":
        return envelope(
            operation,
            "ok",
            {
                "environment_clean": not any(
                    os.environ.get(name)
                    for name in (
                        "GITHUB_TOKEN",
                        "AWS_SECRET_ACCESS_KEY",
                        "PYTHONPATH",
                        "SSH_AUTH_SOCK",
                    )
                ),
                "import_path_clean": not any(
                    "site-packages" in path or "dist-packages" in path
                    for path in sys.path
                ),
                "network": False,
                "status": "verified",
            },
        )
    if operation == "discover":
        return envelope(
            operation,
            "ok",
            {
                "executed": False,
                "roots": inputs["roots"],
                "status": "discovered",
            },
        )
    plan = plan_for(operation, inputs)
    plan_sha256 = sha(canonical(plan))
    if not inputs.get("apply", False):
        return envelope(
            operation,
            "planned",
            {
                "effects": False,
                "plan": plan,
                "plan_sha256": plan_sha256,
                "status": "planned",
            },
        )
    return {
        **envelope(operation, "refused", None),
        "refusal": {"code": "REFUSE_DIRECT_SDK_APPLY"},
    }
