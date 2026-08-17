---
name: "prototype-lock-factory"
description: "Locks an accepted prototype into a canonical project, enforces local-before-cloud causal evidence, prevents post-acceptance scope drift, and exports a hash-verified no-PII handoff."
metadata: {"version": "1.0.1", "author": "RAPP Community", "tags": ["prototype", "factory", "local_first", "acceptance", "handoff", "no_pii"]}
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
8. Promote the sanitized public derivative only after export:
   - validate/test the single-file agent against the public registry SDK;
   - project agent.py -> SKILL.md with the shared converter and prove a
     byte-identical round trip;
   - run the complete public skill validation suite;
   - submit the exact bytes through the registry mutation/receipt path;
   - verify the notarized registry hash and the public skills-repo hash.
9. Commit the canonical private/project source and public derivative with
   provenance. A public receipt is not proof of the private project, and a
   private green suite is not permission to publish customer context.

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

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `prototype_lock_factory_agent.py` and embedded as the fenced Python below (sha256 916f1fb4e63074c6…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `prototype_lock_factory_agent.py` first:

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
8. Promote the sanitized public derivative only after export:
   - validate/test the single-file agent against the public registry SDK;
   - project agent.py -> SKILL.md with the shared converter and prove a
     byte-identical round trip;
   - run the complete public skill validation suite;
   - submit the exact bytes through the registry mutation/receipt path;
   - verify the notarized registry hash and the public skills-repo hash.
9. Commit the canonical private/project source and public derivative with
   provenance. A public receipt is not proof of the private project, and a
   private green suite is not permission to publish customer context.

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
    "name": "@kody-w/prototype_lock_factory_agent",
    "version": "1.0.1",
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
