from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
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


def content(operation, subject=None):
    value = {
        "fixture": "canonical-sdk-boundary",
        "operation": operation,
        "version": 2 if operation == "update" else 1,
    }
    if subject is not None:
        value["subject"] = subject
    return canonical(value) + b"\n"


def scaffold_plan(inputs, identity):
    subject = {
        key: inputs[key]
        for key in ("kind", "mode", "owner_label", "slug", "world_id")
    }
    subject["rappid"] = identity
    files = {
        "install.json": content("scaffold", subject),
        "notes/welcome.txt": b"synthetic scaffold bytes: \xc3\xa9\x00\n",
    }
    if subject["kind"] == "organization":
        files["organization.json"] = canonical(subject) + b"\n"
    return {
        "actions": [
            {
                "bytes": len(after),
                "content_base64": base64.b64encode(after).decode("ascii"),
                "expected_sha256": None,
                "mode": 0o600,
                "operation": "create",
                "path": name,
                "sha256": sha(after),
            }
            for name, after in sorted(files.items())
        ],
        "network": False,
        "operation": "scaffold",
        "preconditions": [{"path": inputs["root"], "state": "absent"}],
        "schema": "rapp-work-plan-fixture/1",
        "subject": subject,
        "target": inputs["root"],
    }


def plan_for(operation, inputs):
    if operation == "scaffold":
        return scaffold_plan(inputs, "fixture-" + uuid.uuid4().hex)
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


def refused(operation, code):
    return {
        **envelope(operation, "refused", None),
        "refusal": {"code": code},
    }


def apply_scaffold(inputs):
    plan = inputs.get("plan")
    if not isinstance(plan, dict) or inputs.get("plan_sha256") != sha(canonical(plan)):
        return refused("scaffold", "REFUSE_PLAN_HASH")
    subject = plan.get("subject")
    if not isinstance(subject, dict):
        return refused("scaffold", "REFUSE_PLAN")
    identity = subject.get("rappid")
    if (
        not isinstance(identity, str)
        or re.fullmatch(r"fixture-[0-9a-f]{32}", identity) is None
        or inputs.get("kind") not in {"workspace", "organization"}
        or inputs.get("mode") not in {"solo", "hive"}
        or canonical(plan) != canonical(scaffold_plan(inputs, identity))
    ):
        return refused("scaffold", "REFUSE_PLAN")
    target = Path(inputs["root"])
    staging = target.parent / f".{target.name}.rapp-work-{inputs['plan_sha256'][:24]}"
    if os.path.lexists(target):
        return refused("scaffold", "REFUSE_CREATE_COLLISION")
    if os.path.lexists(staging):
        return refused("scaffold", "REFUSE_RECOVERY_COLLISION")
    staging.mkdir(mode=0o700)
    try:
        for action in plan["actions"]:
            path = staging / action["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(base64.b64decode(action["content_base64"], validate=True))
            path.chmod(action["mode"])
        if os.path.lexists(target):
            return refused("scaffold", "REFUSE_CREATE_COLLISION")
        # This synthetic harness does not model the native no-replace syscall or crash recovery.
        staging.rename(target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return envelope(
        "scaffold",
        "applied",
        {
            "effects": True,
            "kind": inputs["kind"],
            "plan_sha256": inputs["plan_sha256"],
            "rappid": identity,
            "root": str(target),
            "status": "created",
        },
    )


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
    if operation == "scaffold" and inputs.get("apply") is True:
        return apply_scaffold(inputs)
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
    return refused(operation, "REFUSE_DIRECT_SDK_APPLY")
