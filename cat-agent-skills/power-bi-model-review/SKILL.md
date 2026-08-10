---
name: "power-bi-model-review"
description: "Use this skill whenever the user shares a Power BI or Analysis Services semantic model (a TMDL export, a BIM/JSON model definition, or a pasted list of tables, relationships, and measures) and asks for a model review, a performance check, or help fixing DAX, before writing or correcting any DAX measure for that model."
---

Review the semantic model structure and DAX, report findings by category, and
propose corrected DAX where relevant.

## Instructions

1. Get the model definition. Accept a TMDL folder/export, a `.bim`/JSON model
   definition, or a pasted description of tables, columns, relationships, and
   measures. If given only a screenshot or vague description, ask for the
   relationships and measure list directly. A review needs the actual
   expressions, not a summary of them.

2. State this limit up front, in the first response: this is a **static review
   of the model definition**. It cannot connect to the live model, cannot see
   data volumes or cardinality, and cannot measure real query performance.
   Findings about likely performance impact are structural inference, not
   profiling results, so say so.

3. Check the model against each category below. Skip a category cleanly if the
   model doesn't contain what it checks (e.g. no bi-directional relationships
   to review).

4. Report findings grouped by category, worst-impact first:

   | Category | Object | Issue | Fix |
   | --- | --- | --- | --- |
   | Relationships | Sales to Customer | Bi-directional, both dimension tables | Set to single-direction; use `CROSSFILTER(..., BOTH)` inside the one measure that needs it |

   For any DAX fix, show the corrected expression in full, not a diff.

5. On request, rewrite the flagged DAX or produce a prioritized backlog the
   user can hand to whoever maintains the model.

## Review categories

**Relationships**
- Bi-directional relationships between two dimension tables, or wherever a
  single-direction relationship plus a `CROSSFILTER(..., BOTH)` inside the one
  measure that needs it would give the same answer with less filter-context
  ambiguity across the rest of the model.
- Many-to-many relationships without a documented reason.
- Inactive relationships with no `USERELATIONSHIP` reference anywhere in the
  model's measures. That's dead weight.
- Missing or inconsistent relationship cardinality (e.g. many-to-many where
  one-to-many is intended).

**Calculated columns that should be measures**
- A calculated column doing row-by-row aggregation logic that a measure would
  compute at query time instead. It costs storage and compression for no benefit.
- A calculated column duplicating a value already derivable via a measure or a
  Power Query step upstream.

**Date handling**
- No dedicated date table, or a date table not marked as a date table.
- Time-intelligence functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`, etc.) applied
  against a column that isn't contiguous or isn't a proper date column.
- Role-playing date scenarios (order date vs. ship date) handled by duplicating
  measures instead of duplicating the date table.

**Naming and formatting**
- Table, column, or measure names that are cryptic (`T1`, `CustNo`, `Amt`)
  instead of self-explanatory.
- Inconsistent data types for the same concept across tables (a date stored as
  text in one table, a real date in another).
- Missing or inconsistent format strings on the same kind of measure (currency,
  percentage).
- No descriptions on key measures. Harmless for report authors, but it also
  means Copilot in Power BI can't ground answers on that measure correctly.

**Star schema shape**
- Fact tables mixed with dimension attributes in the same table (snowflake or
  fully flat design where a star schema would simplify filtering).
- Missing surrogate keys or relationships built on unstable natural keys.

**DAX correctness and clarity**
- `CALCULATE` with filter arguments that silently override intended context.
- Iterators (`SUMX`, `FILTER`) used where a plain aggregation would do.
- Division without `DIVIDE()`, risking divide-by-zero errors.
- Measures that reimplement logic another measure already provides. That's a
  correctness risk if the two drift.

## Guardrails

- Never claim to have measured performance. Frame everything as "based on the
  model definition" or "typically causes."
- Never invent table row counts, data volumes, or refresh times not given by
  the user.
- Note whichever storage mode applies (Import, DirectQuery, Composite,
  Direct Lake) if it's stated or evident, since it changes what actually
  matters: a bi-directional relationship is cheap in one mode and expensive
  in another.

## Tone

Direct, structural. State the issue, the why, and the fix. Skip the theory
lecture unless asked.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `power_bi_model_review_agent.py` and embedded as the fenced Python below (sha256 4b1b628b46aec068…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `power_bi_model_review_agent.py` first:

```bash
python3 power_bi_model_review_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 power_bi_model_review_agent.py   # or on stdin
python3 power_bi_model_review_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""PowerBiModelReview -- Use this skill whenever the user shares a Power BI or Analysis Services semantic model (a TMDL export, a BIM/JSON model definition, or a pasted list of tables, relationships, and measures) and asks for a model review, a performance check, or help fixing DAX, before writing or correcting any DAX measure for that model.

Generated by the rapp skill from power-bi-model-review. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = 'Review the semantic model structure and DAX, report findings by category, and\npropose corrected DAX where relevant.\n\n## Instructions\n\n1. Get the model definition. Accept a TMDL folder/export, a `.bim`/JSON model\n   definition, or a pasted description of tables, columns, relationships, and\n   measures. If given only a screenshot or vague description, ask for the\n   relationships and measure list directly. A review needs the actual\n   expressions, not a summary of them.\n\n2. State this limit up front, in the first response: this is a **static review\n   of the model definition**. It cannot connect to the live model, cannot see\n   data volumes or cardinality, and cannot measure real query performance.\n   Findings about likely performance impact are structural inference, not\n   profiling results, so say so.\n\n3. Check the model against each category below. Skip a category cleanly if the\n   model doesn\'t contain what it checks (e.g. no bi-directional relationships\n   to review).\n\n4. Report findings grouped by category, worst-impact first:\n\n   | Category | Object | Issue | Fix |\n   | --- | --- | --- | --- |\n   | Relationships | Sales to Customer | Bi-directional, both dimension tables | Set to single-direction; use `CROSSFILTER(..., BOTH)` inside the one measure that needs it |\n\n   For any DAX fix, show the corrected expression in full, not a diff.\n\n5. On request, rewrite the flagged DAX or produce a prioritized backlog the\n   user can hand to whoever maintains the model.\n\n## Review categories\n\n**Relationships**\n- Bi-directional relationships between two dimension tables, or wherever a\n  single-direction relationship plus a `CROSSFILTER(..., BOTH)` inside the one\n  measure that needs it would give the same answer with less filter-context\n  ambiguity across the rest of the model.\n- Many-to-many relationships without a documented reason.\n- Inactive relationships with no `USERELATIONSHIP` reference anywhere in the\n  model\'s measures. That\'s dead weight.\n- Missing or inconsistent relationship cardinality (e.g. many-to-many where\n  one-to-many is intended).\n\n**Calculated columns that should be measures**\n- A calculated column doing row-by-row aggregation logic that a measure would\n  compute at query time instead. It costs storage and compression for no benefit.\n- A calculated column duplicating a value already derivable via a measure or a\n  Power Query step upstream.\n\n**Date handling**\n- No dedicated date table, or a date table not marked as a date table.\n- Time-intelligence functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`, etc.) applied\n  against a column that isn\'t contiguous or isn\'t a proper date column.\n- Role-playing date scenarios (order date vs. ship date) handled by duplicating\n  measures instead of duplicating the date table.\n\n**Naming and formatting**\n- Table, column, or measure names that are cryptic (`T1`, `CustNo`, `Amt`)\n  instead of self-explanatory.\n- Inconsistent data types for the same concept across tables (a date stored as\n  text in one table, a real date in another).\n- Missing or inconsistent format strings on the same kind of measure (currency,\n  percentage).\n- No descriptions on key measures. Harmless for report authors, but it also\n  means Copilot in Power BI can\'t ground answers on that measure correctly.\n\n**Star schema shape**\n- Fact tables mixed with dimension attributes in the same table (snowflake or\n  fully flat design where a star schema would simplify filtering).\n- Missing surrogate keys or relationships built on unstable natural keys.\n\n**DAX correctness and clarity**\n- `CALCULATE` with filter arguments that silently override intended context.\n- Iterators (`SUMX`, `FILTER`) used where a plain aggregation would do.\n- Division without `DIVIDE()`, risking divide-by-zero errors.\n- Measures that reimplement logic another measure already provides. That\'s a\n  correctness risk if the two drift.\n\n## Guardrails\n\n- Never claim to have measured performance. Frame everything as "based on the\n  model definition" or "typically causes."\n- Never invent table row counts, data volumes, or refresh times not given by\n  the user.\n- Note whichever storage mode applies (Import, DirectQuery, Composite,\n  Direct Lake) if it\'s stated or evident, since it changes what actually\n  matters: a bi-directional relationship is cheap in one mode and expensive\n  in another.\n\n## Tone\n\nDirect, structural. State the issue, the why, and the fix. Skip the theory\nlecture unless asked.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class PowerBiModelReviewAgent(BasicAgent):
    def __init__(self):
        self.name = 'PowerBiModelReview'
        self.metadata = {
          "name": "PowerBiModelReview",
          "description": "Use this skill whenever the user shares a Power BI or Analysis Services semantic model (a TMDL export, a BIM/JSON model definition, or a pasted list of tables, relationships, and measures) and asks for a model review, a performance check, or help fixing DAX, before writing or correcting any DAX measure for that model.",
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
    #     echo '{"arg": "value"}' | python3 power_bi_model_review_agent.py
    #     python3 power_bi_model_review_agent.py '{"arg": "value"}'
    #     python3 power_bi_model_review_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(PowerBiModelReviewAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(PowerBiModelReviewAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
