---
name: "rapp-pipeline"
description: "Run RAPP (Rapid Agent Prototyping Platform) pipeline to generate AI agents from transcripts. Use when building agents, generating Copilot Studio solutions, or deploying to Microsoft AI stack."
allowed-tools: "Bash, Read, Write, Glob, Grep"
---

# RAPP Pipeline Skill

This skill runs the RAPP pipeline to generate production-ready AI agents from business transcripts.

## Available Commands

### Full Pipeline (Transcript to Agent)
```bash
python3 -m rapp_cli pipeline <project_id> [options]
```

Options:
- `-t, --transcript PATH` - Path to transcript file
- `-c, --customer TEXT` - Customer name
- `-o, --output PATH` - Output directory
- `--json-output` - Output results as JSON (for parsing)

### Copilot Studio + Azure DevOps
```bash
python3 -m rapp_cli copilot-studio <project_id> [options]
```

Options:
- `-t, --transcript PATH` - Path to transcript file
- `-c, --customer TEXT` - Customer name
- `-p, --publisher TEXT` - Solution publisher prefix
- `-e, --environments TEXT` - Target environments (comma-separated)
- `--json-output` - Output results as JSON

### Project Management
```bash
# List all projects
python3 -m rapp_cli list-projects --json-output

# Show project details
python3 -m rapp_cli show-project <project_id> --json-output

# Create new project
python3 -m rapp_cli new <project_name>
```

### Quality Gates
```bash
python3 -m rapp_cli quality-gate <project_id> --gate QG1
```

Gates: QG1 (Transcript), QG2 (Customer), QG3 (Code), QG4-QG5 (Demo), QG6 (Deployment)

### Reports
```bash
python3 -m rapp_cli report <project_id> --report-type discovery
```

Types: discovery, mvp, code, qg1-qg6, executive_summary

## Workflow

1. **Create Project**
   ```bash
   python3 -m rapp_cli new my-project
   ```

2. **Add Transcript** (save to `rapp_projects/{project}/inputs/transcript.txt`)

3. **Run Pipeline**
   ```bash
   # Basic agent generation
   python3 -m rapp_cli pipeline my-project --customer "Contoso" --json-output

   # Full Microsoft AI stack
   python3 -m rapp_cli copilot-studio my-project --customer "Contoso" --json-output
   ```

4. **Check Output**
   ```bash
   python3 -m rapp_cli show-project my-project --json-output
   ```

## Output Locations

- Agents: `rapp_projects/{project}/outputs/{agent_id}_agent.py`
- Demos: `rapp_projects/{project}/outputs/{agent_id}_demo.json`
- HTML Tester: `rapp_projects/{project}/outputs/agent_tester.html`
- Copilot Studio: `rapp_projects/{project}/copilot_studio/`
- Azure DevOps: `rapp_projects/{project}/azure_devops/`

## Working Directory

Always run commands from: `~/.rapp/src`

## Example: End-to-End Automation

```bash
cd ~/.rapp/src

# 1. Create project
python3 -m rapp_cli new contoso-agent

# 2. Create transcript (or use existing)
cat > rapp_ai/rapp_projects/contoso-agent/inputs/transcript.txt << 'EOF'
[Discovery call transcript content here]
EOF

# 3. Run full pipeline
python3 -m rapp_cli copilot-studio contoso-agent \
  --customer "Contoso Financial" \
  --publisher contoso \
  --environments "dev,test,prod" \
  --json-output

# 4. Verify outputs
python3 -m rapp_cli show-project contoso-agent --json-output
```

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "project_id": {
      "description": "Derived from `<project_id>` used in the documented command at line 9.",
      "type": "string"
    },
    "project_name": {
      "description": "Derived from `<project_name>` used in the documented command at line 39.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `rapp_pipeline_agent.py` and embedded as the fenced Python below (sha256 0297faabc3c6c46d…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `rapp_pipeline_agent.py` first:

```bash
python3 rapp_pipeline_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 rapp_pipeline_agent.py   # or on stdin
python3 rapp_pipeline_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""RappPipeline -- Run RAPP (Rapid Agent Prototyping Platform) pipeline to generate AI agents from transcripts. Use when building agents, generating Copilot Studio solutions, or deploying to Microsoft AI stack.

Generated by the rapp skill from rapp-pipeline. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE the brainstem -- stay executable anyway.
    class BasicAgent:  # noqa: D101 - minimal stand-in, same contract
        def __init__(self, name=None, metadata=None):
            if name:
                self.name = name
            if metadata:
                self.metadata = metadata

        def perform(self, **kwargs):
            return "Not implemented."

        def system_context(self):
            return None

        def to_tool(self):
            return {"type": "function", "function": {
                "name": self.name,
                "description": self.metadata.get("description", ""),
                "parameters": self.metadata.get("parameters", {})}}

# The procedural layer, verbatim from the source capability. The brainstem
# returns this to the model, so the skill's instructions still drive behaviour
# -- now behind a typed, deterministic tool contract.
INSTRUCTIONS = '# RAPP Pipeline Skill\n\nThis skill runs the RAPP pipeline to generate production-ready AI agents from business transcripts.\n\n## Available Commands\n\n### Full Pipeline (Transcript to Agent)\n```bash\npython3 -m rapp_cli pipeline <project_id> [options]\n```\n\nOptions:\n- `-t, --transcript PATH` - Path to transcript file\n- `-c, --customer TEXT` - Customer name\n- `-o, --output PATH` - Output directory\n- `--json-output` - Output results as JSON (for parsing)\n\n### Copilot Studio + Azure DevOps\n```bash\npython3 -m rapp_cli copilot-studio <project_id> [options]\n```\n\nOptions:\n- `-t, --transcript PATH` - Path to transcript file\n- `-c, --customer TEXT` - Customer name\n- `-p, --publisher TEXT` - Solution publisher prefix\n- `-e, --environments TEXT` - Target environments (comma-separated)\n- `--json-output` - Output results as JSON\n\n### Project Management\n```bash\n# List all projects\npython3 -m rapp_cli list-projects --json-output\n\n# Show project details\npython3 -m rapp_cli show-project <project_id> --json-output\n\n# Create new project\npython3 -m rapp_cli new <project_name>\n```\n\n### Quality Gates\n```bash\npython3 -m rapp_cli quality-gate <project_id> --gate QG1\n```\n\nGates: QG1 (Transcript), QG2 (Customer), QG3 (Code), QG4-QG5 (Demo), QG6 (Deployment)\n\n### Reports\n```bash\npython3 -m rapp_cli report <project_id> --report-type discovery\n```\n\nTypes: discovery, mvp, code, qg1-qg6, executive_summary\n\n## Workflow\n\n1. **Create Project**\n   ```bash\n   python3 -m rapp_cli new my-project\n   ```\n\n2. **Add Transcript** (save to `rapp_projects/{project}/inputs/transcript.txt`)\n\n3. **Run Pipeline**\n   ```bash\n   # Basic agent generation\n   python3 -m rapp_cli pipeline my-project --customer "Contoso" --json-output\n\n   # Full Microsoft AI stack\n   python3 -m rapp_cli copilot-studio my-project --customer "Contoso" --json-output\n   ```\n\n4. **Check Output**\n   ```bash\n   python3 -m rapp_cli show-project my-project --json-output\n   ```\n\n## Output Locations\n\n- Agents: `rapp_projects/{project}/outputs/{agent_id}_agent.py`\n- Demos: `rapp_projects/{project}/outputs/{agent_id}_demo.json`\n- HTML Tester: `rapp_projects/{project}/outputs/agent_tester.html`\n- Copilot Studio: `rapp_projects/{project}/copilot_studio/`\n- Azure DevOps: `rapp_projects/{project}/azure_devops/`\n\n## Working Directory\n\nAlways run commands from: `~/.rapp/src`\n\n## Example: End-to-End Automation\n\n```bash\ncd ~/.rapp/src\n\n# 1. Create project\npython3 -m rapp_cli new contoso-agent\n\n# 2. Create transcript (or use existing)\ncat > rapp_ai/rapp_projects/contoso-agent/inputs/transcript.txt << \'EOF\'\n[Discovery call transcript content here]\nEOF\n\n# 3. Run full pipeline\npython3 -m rapp_cli copilot-studio contoso-agent \\\n  --customer "Contoso Financial" \\\n  --publisher contoso \\\n  --environments "dev,test,prod" \\\n  --json-output\n\n# 4. Verify outputs\npython3 -m rapp_cli show-project contoso-agent --json-output\n```'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = [
    {
        "cmd": "python3 -m rapp_cli pipeline <project_id> [options]",
        "line": 9
    },
    {
        "cmd": "python3 -m rapp_cli copilot-studio <project_id> [options]",
        "line": 20
    },
    {
        "cmd": "python3 -m rapp_cli list-projects --json-output",
        "line": 33
    },
    {
        "cmd": "python3 -m rapp_cli show-project <project_id> --json-output",
        "line": 36
    },
    {
        "cmd": "python3 -m rapp_cli new <project_name>",
        "line": 39
    },
    {
        "cmd": "python3 -m rapp_cli quality-gate <project_id> --gate QG1",
        "line": 44
    },
    {
        "cmd": "python3 -m rapp_cli report <project_id> --report-type discovery",
        "line": 51
    },
    {
        "cmd": "python3 -m rapp_cli new my-project",
        "line": 60
    },
    {
        "cmd": "python3 -m rapp_cli pipeline my-project --customer \"Contoso\" --json-output",
        "line": 68
    },
    {
        "cmd": "python3 -m rapp_cli copilot-studio my-project --customer \"Contoso\" --json-output",
        "line": 71
    },
    {
        "cmd": "python3 -m rapp_cli show-project my-project --json-output",
        "line": 76
    },
    {
        "cmd": "cd ~/.rapp/src",
        "line": 94
    },
    {
        "cmd": "python3 -m rapp_cli new contoso-agent",
        "line": 97
    },
    {
        "cmd": "python3 -m rapp_cli copilot-studio contoso-agent \\",
        "line": 105
    },
    {
        "cmd": "python3 -m rapp_cli show-project contoso-agent --json-output",
        "line": 112
    }
]


class RappPipelineAgent(BasicAgent):
    def __init__(self):
        self.name = 'RappPipeline'
        self.metadata = {
        "name": "RappPipeline",
        "description": "Run RAPP (Rapid Agent Prototyping Platform) pipeline to generate AI agents from transcripts. Use when building agents, generating Copilot Studio solutions, or deploying to Microsoft AI stack.",
        "parameters": {
                "properties": {
                        "project_id": {
                                "description": "Derived from `<project_id>` used in the documented command at line 9.",
                                "type": "string"
                        },
                        "project_name": {
                                "description": "Derived from `<project_name>` used in the documented command at line 39.",
                                "type": "string"
                        }
                },
                "required": [],
                "type": "object"
        }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        missing = [k for k in self.metadata["parameters"].get("required", [])
                   if k not in kwargs]
        if missing:
            return json.dumps({"status": "error",
                               "missing_required": missing}, indent=2)
        resolved, unresolved = [], set()
        for step in STEPS:
            cmd = step["cmd"]
            for key, value in kwargs.items():
                for token in ("<" + key.replace("_", "-") + ">",
                              "<" + key + ">",
                              "{{" + key + "}}",
                              "$" + key.upper()):
                    cmd = cmd.replace(token, str(value))
            for leftover in re.findall(r"<[a-zA-Z][a-zA-Z0-9 _.-]{1,40}>", cmd):
                unresolved.add(leftover)
            resolved.append(cmd)
        return json.dumps({"status": "ok",
                           "steps": resolved,
                           "unresolved_placeholders": sorted(unresolved),
                           "note": "Resolved deterministically by the agent; "
                                   "run in order. Nothing was executed here."},
                          indent=2)

if __name__ == "__main__":
    # Standalone entry point: the deterministic layer runs with NO brainstem,
    # no framework, no install. This is what lets a "simple SKILL.md" platform
    # keep real determinism -- the host model shells out to this file instead
    # of improvising the procedure in prose.
    #     echo '{"arg": "value"}' | python3 rapp_pipeline_agent.py
    #     python3 rapp_pipeline_agent.py '{"arg": "value"}'
    #     python3 rapp_pipeline_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(RappPipelineAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(RappPipelineAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
