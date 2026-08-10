---
name: "lookup-dataverse-table"
description: "Use this skill whenever the user wants to search, browse, or look up records in a Microsoft Dataverse table \u2014 for example \"look up accounts\", \"find opportunities for Contoso\", \"show me contact details\", or \"search cases by status\". Always prefer this skill (which queries Dataverse live via the Dataverse MCP Server) BEFORE answering any question about Dataverse records."
---

Help the user search any Microsoft Dataverse table, browse matching records, and
view full record details — all sourced live from Dataverse via the Dataverse MCP
Server tool.

## Data source (critical)

- Always source data **dynamically** from Microsoft Dataverse using the Dataverse
  MCP Server tool.
- **NEVER** fabricate, invent, hardcode, guess, or reuse records from examples or
  prior general knowledge. Every record and every field value you show must come
  from a live query via the tool.
- If the tool returns no results or fails, say so plainly and ask the user to try
  again or refine their search. Do not make up data.

## Workflow

### Step 1 — Identify the table

- If the user names a table (e.g. "accounts", "opportunities", "contacts"), use
  that table.
- If the user is ambiguous, ask: *"Which table would you like to search? For
  example: contacts, accounts, opportunities, leads, etc."*
- Use `describe('tables/')` to resolve the table's logical name if needed.

### Step 2 — Discover the schema

Before querying, call `describe('tables/{tablename}')` to retrieve:

- The table's **primary name field** (used for display).
- The table's **primary key field** (used internally for record lookup).
- Available columns and their logical names and types.

Note the **primary key field name** (e.g. `accountid`) so you can request its
value when querying. The primary key GUID **values** returned by later queries
stay **internal** — never display them to the user.

### Step 3 — Find records

1. Query the table using `read_query`, always retrieving at least:
   - The **primary name field**
   - A **key identifier field** (e.g. email, account number, status)
   - The **primary key** (for internal use only)
2. Apply any search filters the user provides (name, keyword, status, date range,
   related record, etc.).
3. Return **at most 15 rows**. If more than 15 records match, show the first 15
   and prompt the user to narrow the search.
4. If a field has no value, show `(none)`.

Present results as a numbered markdown list, or a table with a leading number
column so the user can select by number:

| # | Record Name | Key Identifier |
|---|-------------|----------------|
| 1 | Example Corp | account@example.com |
| 2 | Another Record | 555-0100 |

### Step 4 — Select a record

When the user selects a record (by number, name, or identifier):

1. Re-query the Dataverse table using the internally stored primary key GUID.
2. Display the most useful ~20 fields for that record, presented as a readable
   labeled list or table.
3. Omit empty/null fields unless the user requests the full record.
4. Never reveal GUIDs or internal identifiers.

Example detail view:

| Field | Value |
|-------|-------|
| **Name** | Example Corp |
| **Email** | account@example.com |
| **Phone** | 555-0100 |
| **City** | Seattle |
| **State** | WA |

## Remembering preferred fields

- If the user requests a different set of fields (add, remove, or replace),
  **remember those preferences** using memory tools.
- Default to the user's preferred field set on all subsequent detail lookups — in
  this and future conversations — until the user changes it again.

## Supported tables

The skill works with **any** Dataverse table. Common examples:

| Table display name | Logical name |
|--------------------|--------------|
| Contacts | contact |
| Accounts | account |
| Opportunities | opportunity |
| Leads | lead |
| Cases | incident |
| Products | product |
| Orders | salesorder |
| Invoices | invoice |
| Activities | activitypointer |
| Users | systemuser |

Use `describe('tables/')` to discover all available tables in the environment.

## Guardrails

- Present matching records as a numbered markdown list, or a table with a leading
  number column (# / Record Name / Key Identifier).
- Do **not** expose raw GUIDs, internal IDs, query syntax, or raw tool payloads
  to the user.
- Do **not** emit adaptive card or suggested-action code blocks.
- When a search yields no results, say so clearly and suggest alternative search
  terms.
- When a table is not found, suggest similar table names or ask the user to
  clarify.
- When more than 15 records match, always prompt the user to refine the search
  rather than paginating silently.

## Tone

Be concise and helpful. Explain uncertainty rather than hiding it, and never
present fabricated data as if it came from Dataverse.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `lookup_dataverse_table_agent.py` and embedded as the fenced Python below (sha256 ac816289aaff0d48…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `lookup_dataverse_table_agent.py` first:

```bash
python3 lookup_dataverse_table_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 lookup_dataverse_table_agent.py   # or on stdin
python3 lookup_dataverse_table_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""LookupDataverseTable -- Use this skill whenever the user wants to search, browse, or look up records in a Microsoft Dataverse table — for example "look up accounts", "find opportunities for Contoso", "show me contact details", or "search cases by status". Always prefer this skill (which queries Dataverse live via the Dataverse MCP Server) BEFORE answering any question about Dataverse records.

Generated by the rapp skill from lookup-dataverse-table. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

import json
import re
import sys

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # running OUTSIDE a brainstem -- stay executable anyway.
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

# The procedural layer, verbatim from the source capability.
INSTRUCTIONS = 'Help the user search any Microsoft Dataverse table, browse matching records, and\nview full record details — all sourced live from Dataverse via the Dataverse MCP\nServer tool.\n\n## Data source (critical)\n\n- Always source data **dynamically** from Microsoft Dataverse using the Dataverse\n  MCP Server tool.\n- **NEVER** fabricate, invent, hardcode, guess, or reuse records from examples or\n  prior general knowledge. Every record and every field value you show must come\n  from a live query via the tool.\n- If the tool returns no results or fails, say so plainly and ask the user to try\n  again or refine their search. Do not make up data.\n\n## Workflow\n\n### Step 1 — Identify the table\n\n- If the user names a table (e.g. "accounts", "opportunities", "contacts"), use\n  that table.\n- If the user is ambiguous, ask: *"Which table would you like to search? For\n  example: contacts, accounts, opportunities, leads, etc."*\n- Use `describe(\'tables/\')` to resolve the table\'s logical name if needed.\n\n### Step 2 — Discover the schema\n\nBefore querying, call `describe(\'tables/{tablename}\')` to retrieve:\n\n- The table\'s **primary name field** (used for display).\n- The table\'s **primary key field** (used internally for record lookup).\n- Available columns and their logical names and types.\n\nNote the **primary key field name** (e.g. `accountid`) so you can request its\nvalue when querying. The primary key GUID **values** returned by later queries\nstay **internal** — never display them to the user.\n\n### Step 3 — Find records\n\n1. Query the table using `read_query`, always retrieving at least:\n   - The **primary name field**\n   - A **key identifier field** (e.g. email, account number, status)\n   - The **primary key** (for internal use only)\n2. Apply any search filters the user provides (name, keyword, status, date range,\n   related record, etc.).\n3. Return **at most 15 rows**. If more than 15 records match, show the first 15\n   and prompt the user to narrow the search.\n4. If a field has no value, show `(none)`.\n\nPresent results as a numbered markdown list, or a table with a leading number\ncolumn so the user can select by number:\n\n| # | Record Name | Key Identifier |\n|---|-------------|----------------|\n| 1 | Example Corp | account@example.com |\n| 2 | Another Record | 555-0100 |\n\n### Step 4 — Select a record\n\nWhen the user selects a record (by number, name, or identifier):\n\n1. Re-query the Dataverse table using the internally stored primary key GUID.\n2. Display the most useful ~20 fields for that record, presented as a readable\n   labeled list or table.\n3. Omit empty/null fields unless the user requests the full record.\n4. Never reveal GUIDs or internal identifiers.\n\nExample detail view:\n\n| Field | Value |\n|-------|-------|\n| **Name** | Example Corp |\n| **Email** | account@example.com |\n| **Phone** | 555-0100 |\n| **City** | Seattle |\n| **State** | WA |\n\n## Remembering preferred fields\n\n- If the user requests a different set of fields (add, remove, or replace),\n  **remember those preferences** using memory tools.\n- Default to the user\'s preferred field set on all subsequent detail lookups — in\n  this and future conversations — until the user changes it again.\n\n## Supported tables\n\nThe skill works with **any** Dataverse table. Common examples:\n\n| Table display name | Logical name |\n|--------------------|--------------|\n| Contacts | contact |\n| Accounts | account |\n| Opportunities | opportunity |\n| Leads | lead |\n| Cases | incident |\n| Products | product |\n| Orders | salesorder |\n| Invoices | invoice |\n| Activities | activitypointer |\n| Users | systemuser |\n\nUse `describe(\'tables/\')` to discover all available tables in the environment.\n\n## Guardrails\n\n- Present matching records as a numbered markdown list, or a table with a leading\n  number column (# / Record Name / Key Identifier).\n- Do **not** expose raw GUIDs, internal IDs, query syntax, or raw tool payloads\n  to the user.\n- Do **not** emit adaptive card or suggested-action code blocks.\n- When a search yields no results, say so clearly and suggest alternative search\n  terms.\n- When a table is not found, suggest similar table names or ask the user to\n  clarify.\n- When more than 15 records match, always prompt the user to refine the search\n  rather than paginating silently.\n\n## Tone\n\nBe concise and helpful. Explain uncertainty rather than hiding it, and never\npresent fabricated data as if it came from Dataverse.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class LookupDataverseTableAgent(BasicAgent):
    def __init__(self):
        self.name = 'LookupDataverseTable'
        self.metadata = {
          "name": "LookupDataverseTable",
          "description": "Use this skill whenever the user wants to search, browse, or look up records in a Microsoft Dataverse table \u2014 for example \"look up accounts\", \"find opportunities for Contoso\", \"show me contact details\", or \"search cases by status\". Always prefer this skill (which queries Dataverse live via the Dataverse MCP Server) BEFORE answering any question about Dataverse records.",
          "parameters": {
            "type": "object",
            "properties": {},
            "required": []
          }
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):  # toaster:generated-perform
        return json.dumps({"status": "ok", "instructions": INSTRUCTIONS,
                           "inputs": kwargs,
                           "note": "Prose-only capability: follow INSTRUCTIONS "
                                   "with the given inputs."}, indent=2)

if __name__ == "__main__":
    #     echo '{"arg": "value"}' | python3 lookup_dataverse_table_agent.py
    #     python3 lookup_dataverse_table_agent.py '{"arg": "value"}'
    #     python3 lookup_dataverse_table_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(LookupDataverseTableAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(LookupDataverseTableAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
