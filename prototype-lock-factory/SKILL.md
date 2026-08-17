---
name: "prototype-lock-factory"
description: "Locks an accepted prototype into a canonical project, enforces local-before-cloud causal evidence, prevents post-acceptance scope drift, and exports a hash-verified no-PII handoff."
metadata: {"author": "RAPP Community", "tags": ["prototype", "factory", "local_first", "acceptance", "handoff", "no_pii"]}
---

Prototype Lock Factory — freeze an accepted prototype into a public handoff.

Use this after a prototype finally behaves correctly and before anyone adds
"one more impressive feature." The accepted transcript becomes authority.

Process:
1. Capture the business workflow, adapter boundary, specialist roster, human
   decisions, immutable transport, and exact approved transcript.
2. Create one canonical `rapp_projects/<slug>/` source with `agents/`,
   `inputs/`, `outputs/`, `exports/`, `PROCESS_CONTRACT.json`, and
   `APPROVED_TRANSCRIPT.md`.
3. Keep transport dumb. The function/agents own routing and business logic.
   `user_guid` may partition memory and workflow state; it never selects agents.
4. Test T1 local/direct first. Require the real natural prompts, truthful
   specialist trace, editable artifacts, downloaded hashes, visual inspection,
   reset, and a causal input -> calculation -> output delta.
5. Only after T1 passes, run the identical T2 cloud gate. Test an immutable T3
   harness last and never debug business logic through it.
6. Once the transcript is accepted, treat later scope as a new version. Do not
   silently replace the approved ending, prompts, artifacts, or human boundary.
7. Export only canonical agents, contracts, evidence receipts, and hashes.
   Public export refuses obvious secrets and requires no customer, employee,
   tenant, subscription, endpoint, phone, or email identifiers.

The agent is offline and standard-library only. It scaffolds and gates files;
the host executes the commands named by the contract and supplies measured
evidence back to operation=gate or operation=run.

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "contract_json": {
      "type": "string"
    },
    "evidence_json": {
      "type": "string"
    },
    "operation": {
      "enum": [
        "describe",
        "plan",
        "scaffold",
        "gate",
        "export",
        "run"
      ],
      "type": "string"
    },
    "output_dir": {
      "type": "string"
    }
  },
  "required": [
    "operation"
  ],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `prototype_lock_factory_agent.py` and embedded as the fenced Python below (sha256 0ac389e3330a65dd…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `prototype_lock_factory_agent.py` first:

```bash
python3 prototype_lock_factory_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 prototype_lock_factory_agent.py   # or on stdin
python3 prototype_lock_factory_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""Prototype Lock Factory — freeze an accepted prototype into a public handoff.

Use this after a prototype finally behaves correctly and before anyone adds
"one more impressive feature." The accepted transcript becomes authority.

Process:
1. Capture the business workflow, adapter boundary, specialist roster, human
   decisions, immutable transport, and exact approved transcript.
2. Create one canonical `rapp_projects/<slug>/` source with `agents/`,
   `inputs/`, `outputs/`, `exports/`, `PROCESS_CONTRACT.json`, and
   `APPROVED_TRANSCRIPT.md`.
3. Keep transport dumb. The function/agents own routing and business logic.
   `user_guid` may partition memory and workflow state; it never selects agents.
4. Test T1 local/direct first. Require the real natural prompts, truthful
   specialist trace, editable artifacts, downloaded hashes, visual inspection,
   reset, and a causal input -> calculation -> output delta.
5. Only after T1 passes, run the identical T2 cloud gate. Test an immutable T3
   harness last and never debug business logic through it.
6. Once the transcript is accepted, treat later scope as a new version. Do not
   silently replace the approved ending, prompts, artifacts, or human boundary.
7. Export only canonical agents, contracts, evidence receipts, and hashes.
   Public export refuses obvious secrets and requires no customer, employee,
   tenant, subscription, endpoint, phone, or email identifiers.

The agent is offline and standard-library only. It scaffolds and gates files;
the host executes the commands named by the contract and supplies measured
evidence back to operation=gate or operation=run.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name = name
            self.metadata = metadata or {}

        def to_tool(self):
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.metadata.get("description", ""),
                    "parameters": self.metadata.get("parameters", {}),
                },
            }


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/prototype_lock_factory",
    "version": "1.0.0",
    "display_name": "Prototype Lock Factory",
    "description": (
        "Locks an accepted prototype into a canonical project, enforces "
        "local-before-cloud causal evidence, prevents post-acceptance scope "
        "drift, and exports a hash-verified no-PII handoff."
    ),
    "author": "RAPP Community",
    "tags": [
        "prototype",
        "factory",
        "local_first",
        "acceptance",
        "handoff",
        "no_pii",
    ],
    "category": "pipeline",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic_agent"],
    "example_call": {
        "args": {
            "operation": "plan",
            "contract_json": (
                "{\"schema\":\"rapp-prototype-process/1.0\","
                "\"project_slug\":\"sample_project\"}"
            ),
        }
    },
}


SCHEMA = "rapp-prototype-process/1.0"
INVARIANTS = (
    "immutable_transport",
    "local_first",
    "one_specialist_per_turn",
    "user_guid_partition_only",
    "human_approval",
    "artifact_delta",
    "reset_supported",
    "canonical_project_source",
)
SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{1,79}$")
PUBLIC_DENY = re.compile(
    r"(?i)(client[_-]?secret|api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|x-functions-key|tenant[_-]?id|"
    r"subscription[_-]?id)\s*[:=]\s*[\"']?[^\"'\s]+"
)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load(value, field):
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a JSON object, string, or path")
    path = Path(value).expanduser()
    text = path.read_text(encoding="utf-8") if path.is_file() else value
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{field} must decode to an object")
    return parsed


def _errors(contract):
    errors = []
    if contract.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    slug = str(contract.get("project_slug") or "")
    if not SLUG.fullmatch(slug):
        errors.append("project_slug must be lowercase snake/kebab case")
    for field in ("display_name", "business_workflow", "adapter_boundary"):
        if not contract.get(field):
            errors.append(f"{field} is required")
    invariants = contract.get("invariants")
    if not isinstance(invariants, dict):
        errors.append("invariants must be an object")
    else:
        for name in INVARIANTS:
            if invariants.get(name) is not True:
                errors.append(f"invariants.{name} must be true")
    specialists = contract.get("specialists")
    if not isinstance(specialists, list) or not specialists:
        errors.append("specialists must be a non-empty array")
    else:
        for index, specialist in enumerate(specialists):
            if not isinstance(specialist, dict):
                errors.append(f"specialists[{index}] must be an object")
            elif not str(specialist.get("file") or "").endswith("_agent.py"):
                errors.append(
                    f"specialists[{index}].file must end with _agent.py"
                )
    turns = contract.get("approved_transcript")
    if not isinstance(turns, list) or not turns:
        errors.append("approved_transcript must be non-empty")
    else:
        for index, turn in enumerate(turns):
            if not isinstance(turn, dict):
                errors.append(f"approved_transcript[{index}] must be an object")
                continue
            for field in ("prompt", "expected_agent", "assertions"):
                if not turn.get(field):
                    errors.append(
                        f"approved_transcript[{index}].{field} is required"
                    )
    transport = contract.get("transport_contract")
    if not isinstance(transport, dict) or transport.get("immutable") is not True:
        errors.append("transport_contract.immutable must be true")
    return errors


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def _write_json(path, value):
    _write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _transcript(contract):
    lines = [
        f"# Approved workflow: {contract['display_name']}",
        "",
        "| Turn | Prompt | Expected agent | Assertions |",
        "|---:|---|---|---|",
    ]
    for index, turn in enumerate(contract["approved_transcript"], 1):
        prompt = str(turn["prompt"]).replace("|", "\\|")
        assertions = "; ".join(
            str(item).replace("|", "\\|") for item in turn["assertions"]
        )
        lines.append(
            f"| {index} | {prompt} | `{turn['expected_agent']}` | "
            f"{assertions} |"
        )
    return "\n".join(lines) + "\n"


def _evidence_errors(evidence, contract):
    errors = []
    local = evidence.get("local")
    if not isinstance(local, dict) or local.get("passed") is not True:
        errors.append("T1 local evidence must pass first")
    for field in ("artifact_hashes", "visible_agent_trace", "causal_delta"):
        if not evidence.get(field):
            errors.append(f"{field} proof is required")
    gates = contract.get("gates") or {}
    if gates.get("require_cloud"):
        cloud = evidence.get("cloud")
        if not isinstance(cloud, dict) or cloud.get("passed") is not True:
            errors.append("T2 cloud evidence is required")
    if gates.get("require_transport"):
        transport = evidence.get("transport")
        if (
            not isinstance(transport, dict)
            or transport.get("passed") is not True
            or transport.get("wire_changed") is not False
        ):
            errors.append(
                "T3 transport must pass with wire_changed=false"
            )
    return errors


def _scan(project):
    findings = []
    for path in project.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".py",
            ".json",
            ".md",
            ".yml",
            ".yaml",
        }:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if PUBLIC_DENY.search(text):
            findings.append(str(path.relative_to(project)))
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                findings.append(f"{path.name}: {exc}")
    return findings


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _export(project):
    archive = project / "exports" / (
        project.name.replace("-", "_") + "_approved_agents.zip"
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as target:
        for path in sorted(project.rglob("*")):
            if not path.is_file() or "exports" in path.parts:
                continue
            if "__pycache__" in path.parts:
                continue
            name = str(path.relative_to(project.parent))
            target.write(path, name)
            manifest[name] = _sha(path)
    _write_json(project / "exports" / "SHA256SUMS.json", manifest)
    return {
        "archive": str(archive),
        "sha256": _sha(archive),
        "members": len(manifest),
    }


class PrototypeLockFactoryAgent(BasicAgent):
    def __init__(self):
        self.name = "PrototypeLockFactory"
        self.metadata = {
            "name": self.name,
            "display_name": __manifest__["display_name"],
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "describe",
                            "plan",
                            "scaffold",
                            "gate",
                            "export",
                            "run",
                        ],
                    },
                    "contract_json": {"type": "string"},
                    "evidence_json": {"type": "string"},
                    "output_dir": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        operation = str(kwargs.get("operation") or "describe").lower()
        if operation == "describe":
            return json.dumps(
                {
                    "status": "ok",
                    "package": __manifest__["name"],
                    "version": __manifest__["version"],
                    "instructions": __doc__,
                },
                indent=2,
            )
        try:
            contract = _load(kwargs.get("contract_json"), "contract_json")
            errors = _errors(contract)
            if errors:
                return json.dumps(
                    {"status": "refused", "stage": "contract", "errors": errors},
                    indent=2,
                )
            if operation == "plan":
                return json.dumps(
                    {
                        "status": "ok",
                        "stages": [
                            "contract",
                            "scaffold",
                            "T1 local evidence",
                            "T2 cloud evidence",
                            "T3 immutable transport evidence",
                            "no-PII export",
                        ],
                        "project_slug": contract["project_slug"],
                    },
                    indent=2,
                )
            output = Path(kwargs.get("output_dir") or ".").expanduser().resolve()
            project = output / contract["project_slug"]
            if operation in {"scaffold", "run"}:
                for name in (
                    "inputs",
                    "agents",
                    "outputs",
                    "exports",
                    "tests",
                ):
                    (project / name).mkdir(parents=True, exist_ok=True)
                _write_json(project / "PROCESS_CONTRACT.json", contract)
                _write(
                    project / "APPROVED_TRANSCRIPT.md",
                    _transcript(contract),
                )
                _write_json(
                    project / "project_config.json",
                    {
                        "guid": contract["project_slug"],
                        "name": contract["display_name"],
                        "enabled_agents": [
                            item["file"] for item in contract["specialists"]
                        ],
                        "behavior_contract": "APPROVED_TRANSCRIPT.md",
                    },
                )
                if operation == "scaffold":
                    return json.dumps(
                        {"status": "success", "project_dir": str(project)},
                        indent=2,
                    )
            if operation in {"gate", "run"}:
                evidence = _load(
                    kwargs.get("evidence_json"),
                    "evidence_json",
                )
                findings = _scan(project)
                gate_errors = _evidence_errors(evidence, contract) + findings
                receipt = {
                    "schema": "rapp-prototype-acceptance/1.0",
                    "status": "success" if not gate_errors else "refused",
                    "errors": gate_errors,
                    "evidence": evidence,
                    "checked_at": _now(),
                }
                _write_json(
                    project / "outputs" / "acceptance_receipt.json",
                    receipt,
                )
                if gate_errors:
                    return json.dumps(receipt, indent=2)
                if operation == "gate":
                    return json.dumps(receipt, indent=2)
            if operation in {"export", "run"}:
                receipt_path = (
                    project / "outputs" / "acceptance_receipt.json"
                )
                if not receipt_path.is_file():
                    return json.dumps(
                        {
                            "status": "refused",
                            "stage": "export",
                            "message": "Passing acceptance receipt required.",
                        },
                        indent=2,
                    )
                receipt = json.loads(
                    receipt_path.read_text(encoding="utf-8")
                )
                if receipt.get("status") != "success":
                    return json.dumps(
                        {
                            "status": "refused",
                            "stage": "export",
                            "message": "Acceptance receipt did not pass.",
                        },
                        indent=2,
                    )
                return json.dumps(
                    {"status": "success", "export": _export(project)},
                    indent=2,
                )
            raise ValueError(f"Unknown operation: {operation}")
        except (OSError, ValueError, KeyError) as exc:
            return json.dumps(
                {"status": "error", "message": str(exc)},
                indent=2,
            )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--tool":
        print(json.dumps(PrototypeLockFactoryAgent().to_tool(), indent=2))
    else:
        raw = sys.argv[1] if len(sys.argv) > 1 else (
            sys.stdin.read().strip() or "{}"
        )
        print(PrototypeLockFactoryAgent().perform(**json.loads(raw)))
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
