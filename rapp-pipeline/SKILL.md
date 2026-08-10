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

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `rapp_pipeline_agent.py` and embedded as the fenced Python below (sha256 1829ab329ec3a2c8…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `rapp_pipeline_agent.py` first:

```bash
python3 rapp_pipeline_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 rapp_pipeline_agent.py   # or on stdin
python3 rapp_pipeline_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""RappPipeline -- Run RAPP (Rapid Agent Prototyping Platform) pipeline to generate AI agents from transcripts. Use when building agents, generating Copilot Studio solutions, or deploying to Microsoft AI stack.

Generated by agentshim from rapp-pipeline. The RCI capsule at the bottom of this file carries the full original; `agentshim.py convert` restores it byte-exact."""

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
