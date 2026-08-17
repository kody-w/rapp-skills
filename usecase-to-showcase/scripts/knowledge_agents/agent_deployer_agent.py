"""AgentDeployer — the lightning loop: hot-deploy agent code into the RUNNING app.

Writes a *_agent.py file into the platform's Azure Files agents/ share and busts the
in-process agent cache, so the new/changed agent serves on the very next request — no
function redeploy, no Copilot Studio solution reimport. The M365 channel is imported
once; iteration happens here, in seconds.

Security model: this is deliberate remote code deployment, gated by the function key
(AuthLevel.FUNCTION) exactly like every other endpoint on the platform. Use it in demo
and prototyping harnesses; disable (delete this file) for hardened production.

Stdlib-only, and can itself be hot-deployed.
"""
import ast
import json

from agents.basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager

AGENTS_DIR = "agents"


class AgentDeployerAgent(BasicAgent):
    def __init__(self):
        self.name = "AgentDeployer"
        self.metadata = {
            "name": self.name,
            "description": (
                "Hot-deploys, lists, or removes agent code files in the platform's live "
                "agents/ store. Use when asked to deploy/update/push an agent, list deployed "
                "agents, or remove one. Changes serve on the next request — no redeploy."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["deploy", "list", "remove"],
                        "description": "deploy = write python_code as file_name and reload; list = show deployed agent files; remove = delete file_name and reload",
                    },
                    "file_name": {
                        "type": "string",
                        "description": "Agent file name, must end in _agent.py (e.g. weather_agent.py)",
                    },
                    "python_code": {
                        "type": "string",
                        "description": "Complete python source for the agent (a BasicAgent subclass). Required for deploy.",
                    },
                },
                "required": ["action"],
            },
        }
        super().__init__(self.name, self.metadata)

    def _bust_cache(self):
        """Force the running app to reload agents on the next request."""
        try:
            import function_app  # already initialized in-process; lazy to avoid import cycles
            function_app._reset_agents_cache()
            return True
        except Exception:
            return False  # standalone/test context — TTL (5 min) will pick it up

    def perform(self, **kwargs):
        action = kwargs.get("action", "list")
        storage = get_storage_manager()

        if action == "list":
            try:
                files = [f.name for f in storage.list_files(AGENTS_DIR)
                         if f.name.endswith("_agent.py")]
            except Exception as e:
                return json.dumps({"error": f"Could not list agents: {e}"})
            return json.dumps({"status": "success", "deployed_agent_files": sorted(files)})

        file_name = str(kwargs.get("file_name", "")).strip()
        if not file_name.endswith("_agent.py") or "/" in file_name or "\\" in file_name or ".." in file_name:
            return json.dumps({"error": "file_name must be a bare file ending in _agent.py"})

        if action == "remove":
            ok = storage.delete_file(AGENTS_DIR, file_name)
            reloaded = self._bust_cache()
            return json.dumps({"status": "success" if ok else "error",
                               "removed": file_name if ok else None,
                               "live_reload": reloaded})

        if action == "deploy":
            code = kwargs.get("python_code", "")
            if not code.strip():
                return json.dumps({"error": "python_code is required for deploy"})
            try:
                ast.parse(code)  # syntax gate before it can ever load
            except SyntaxError as e:
                return json.dumps({"error": f"python_code has a syntax error: {e}"})
            if "BasicAgent" not in code:
                return json.dumps({"error": "python_code must define a BasicAgent subclass"})
            ok = storage.write_file(AGENTS_DIR, file_name, code)
            reloaded = self._bust_cache()
            return json.dumps({
                "status": "success" if ok else "error",
                "deployed": file_name if ok else None,
                "live_reload": reloaded,
                "note": "Agent serves on the next request." if reloaded else
                        "Written; cache refreshes within 5 minutes.",
            })

        return json.dumps({"error": f"Unknown action '{action}'. Use deploy, list, or remove."})
