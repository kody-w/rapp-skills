---
name: "global-greenwashing-claim-auditor"
description: "Use this skill whenever the user asks to audit, scan, review, classify, or de-risk environmental, sustainability, climate, circularity, recycling, emissions, or green marketing claims in pasted conversational content, CSV files, XLSX workbooks, DOCX documents, PPTX presentations, or website URLs. Report universal vocabulary risks separately from Canadian (CA), European Union (EU), and United Kingdom (UK) legal and guidance findings."
---

# Global Greenwashing Claim Auditor

Audit public-facing environmental claims using the bundled global vocabulary, regional taxonomy, legal research, and detection method. Treat the result as compliance triage, not legal advice.

## Required references

Read these before making final findings:

1. `references/Greenwashing-vocab.md`
2. `references/greenwashing-risk-taxonomy.md`
3. `references/greenwashing-detection.md`
4. `references/greenwashing-analysis-research.md`

Use `ANY` only for universal vocabulary and claim-construction risks. Use `CA`, `EU`, and `UK` only when the corresponding regional rule, law, regulation, or guidance supports the finding.

## Workflow

1. Determine the input type and intended markets. If markets are unknown, analyze `ANY`, `CA`, `EU`, and `UK`, but mark regional applicability as unconfirmed.
2. Extract all claim-bearing text while preserving source locations:
   - CSV: row and column.
   - XLSX: sheet and cell.
   - DOCX: paragraph or table cell.
   - PPTX: slide and shape.
   - Conversation: supplied text block.
   - URL: page URL and extracted block.
3. Run the matching script for first-pass triage.
4. Review every flagged unit against the full references. Keyword matches are leads, not verdicts.
5. Add claims missed by keywords, including implied claims, imagery, omissions, comparisons, labels, scope overreach, lifecycle issues, and unsupported future commitments.
6. Report separate findings for every applicable jurisdiction and retain the highest risk as the overall rating.
7. Suggest a bounded rewrite, but never invent evidence, percentages, certifications, methods, or environmental benefits.

## Scripts

Run scripts from the skill directory with Python 3. Use workspace-relative paths so commands remain portable across supported environments.

### CSV

```sh
python scripts/analyze_csv.py "claims.csv" --jurisdictions CA EU UK --out audit.json
```

Use `--text-column NAME` repeatedly to choose columns. Without it, the script scans text-like columns and then all string columns if necessary.

### XLSX

```sh
python scripts/analyze_xlsx.py "claims.xlsx" --sheet "Posts" --jurisdictions CA EU UK --out audit.json
```

Use `--max-items 1000` for a bounded first pass.

### DOCX

```sh
python scripts/analyze_docx.py "document.docx" --jurisdictions CA EU UK --out audit.json
```

### PPTX

```sh
python scripts/analyze_pptx.py "presentation.pptx" --jurisdictions CA EU UK --out audit.json
```

### Conversational content

For short content, analyze it directly using the references. For repeatable scripted triage:

```sh
python scripts/analyze_text.py --text "Our product is carbon neutral and eco-friendly." --jurisdictions CA EU UK --out audit.json
```

For long content:

```sh
python scripts/analyze_text.py --text-file "content.txt" --jurisdictions CA EU UK --out audit.json
```

### Website URL

```sh
python scripts/analyze_url.py "https://example.com/product" --jurisdictions CA EU UK --out audit.json
```

Only fetch public HTTP/HTTPS pages. Do not attempt to bypass authentication, paywalls, robots controls, or access restrictions.

### Markdown output

All entry scripts accept `--format markdown`:

```sh
python scripts/analyze_docx.py "document.docx" --format markdown --out audit.md
```

## Review requirements

Always manually inspect:

- Red findings.
- Generic claims such as `green`, `eco-friendly`, and `sustainable`.
- Carbon-neutral, climate-neutral, net-zero, or offset claims.
- Sustainability labels, seals, certifications, and badges.
- Recyclable, compostable, biodegradable, reusable, and circularity claims.
- Comparisons and future targets.
- Qualifications in footnotes, small print, links, notes, or other slides/pages.

Apply date-sensitive EU rules using the content's intended publication date. If no date is supplied, use the current date and state that assumption.

## Output

Return:

1. Scope, sources, assumed publication date, and applicable jurisdictions.
2. Counts by overall risk and jurisdiction tag.
3. One finding per claim and region, including exact quote, source location, finding code, risk, basis, reason, and remediation.
4. Highest-priority fixes.
5. Limitations, inaccessible evidence, and items requiring legal or technical review.

## Guardrails

- Do not describe `ANY` as a legal violation.
- Do not declare legal compliance; state that no issue was detected under the checks performed.
- Do not treat a keyword match alone as proof of greenwashing.
- Do not invent or assume substantiation.
- Do not ignore visual or contextual implications merely because extracted text appears qualified.
- Do not apply withdrawn proposed legislation as enacted law.
- Escalate high-risk claims for qualified legal review before publication.

## Tone

Be precise, evidence-led, constructive, and explicit about jurisdiction. Every Yellow or Red finding should include a practical remediation.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `global_greenwashing_claim_auditor_agent.py` and embedded as the fenced Python below (sha256 2b240e6d663efe17…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `global_greenwashing_claim_auditor_agent.py` first:

```bash
python3 global_greenwashing_claim_auditor_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 global_greenwashing_claim_auditor_agent.py   # or on stdin
python3 global_greenwashing_claim_auditor_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""GlobalGreenwashingClaimAuditor -- Use this skill whenever the user asks to audit, scan, review, classify, or de-risk environmental, sustainability, climate, circularity, recycling, emissions, or green marketing claims in pasted conversational content, CSV files, XLSX workbooks, DOCX documents, PPTX presentations, or website URLs. Report universal vocabulary risks separately from Canadian (CA), European Union (EU), and United Kingdom (UK) legal and guidance findings.

Generated by the rapp skill from global-greenwashing-claim-auditor. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Global Greenwashing Claim Auditor\n\nAudit public-facing environmental claims using the bundled global vocabulary, regional taxonomy, legal research, and detection method. Treat the result as compliance triage, not legal advice.\n\n## Required references\n\nRead these before making final findings:\n\n1. `references/Greenwashing-vocab.md`\n2. `references/greenwashing-risk-taxonomy.md`\n3. `references/greenwashing-detection.md`\n4. `references/greenwashing-analysis-research.md`\n\nUse `ANY` only for universal vocabulary and claim-construction risks. Use `CA`, `EU`, and `UK` only when the corresponding regional rule, law, regulation, or guidance supports the finding.\n\n## Workflow\n\n1. Determine the input type and intended markets. If markets are unknown, analyze `ANY`, `CA`, `EU`, and `UK`, but mark regional applicability as unconfirmed.\n2. Extract all claim-bearing text while preserving source locations:\n   - CSV: row and column.\n   - XLSX: sheet and cell.\n   - DOCX: paragraph or table cell.\n   - PPTX: slide and shape.\n   - Conversation: supplied text block.\n   - URL: page URL and extracted block.\n3. Run the matching script for first-pass triage.\n4. Review every flagged unit against the full references. Keyword matches are leads, not verdicts.\n5. Add claims missed by keywords, including implied claims, imagery, omissions, comparisons, labels, scope overreach, lifecycle issues, and unsupported future commitments.\n6. Report separate findings for every applicable jurisdiction and retain the highest risk as the overall rating.\n7. Suggest a bounded rewrite, but never invent evidence, percentages, certifications, methods, or environmental benefits.\n\n## Scripts\n\nRun scripts from the skill directory with Python 3. Use workspace-relative paths so commands remain portable across supported environments.\n\n### CSV\n\n```sh\npython scripts/analyze_csv.py "claims.csv" --jurisdictions CA EU UK --out audit.json\n```\n\nUse `--text-column NAME` repeatedly to choose columns. Without it, the script scans text-like columns and then all string columns if necessary.\n\n### XLSX\n\n```sh\npython scripts/analyze_xlsx.py "claims.xlsx" --sheet "Posts" --jurisdictions CA EU UK --out audit.json\n```\n\nUse `--max-items 1000` for a bounded first pass.\n\n### DOCX\n\n```sh\npython scripts/analyze_docx.py "document.docx" --jurisdictions CA EU UK --out audit.json\n```\n\n### PPTX\n\n```sh\npython scripts/analyze_pptx.py "presentation.pptx" --jurisdictions CA EU UK --out audit.json\n```\n\n### Conversational content\n\nFor short content, analyze it directly using the references. For repeatable scripted triage:\n\n```sh\npython scripts/analyze_text.py --text "Our product is carbon neutral and eco-friendly." --jurisdictions CA EU UK --out audit.json\n```\n\nFor long content:\n\n```sh\npython scripts/analyze_text.py --text-file "content.txt" --jurisdictions CA EU UK --out audit.json\n```\n\n### Website URL\n\n```sh\npython scripts/analyze_url.py "https://example.com/product" --jurisdictions CA EU UK --out audit.json\n```\n\nOnly fetch public HTTP/HTTPS pages. Do not attempt to bypass authentication, paywalls, robots controls, or access restrictions.\n\n### Markdown output\n\nAll entry scripts accept `--format markdown`:\n\n```sh\npython scripts/analyze_docx.py "document.docx" --format markdown --out audit.md\n```\n\n## Review requirements\n\nAlways manually inspect:\n\n- Red findings.\n- Generic claims such as `green`, `eco-friendly`, and `sustainable`.\n- Carbon-neutral, climate-neutral, net-zero, or offset claims.\n- Sustainability labels, seals, certifications, and badges.\n- Recyclable, compostable, biodegradable, reusable, and circularity claims.\n- Comparisons and future targets.\n- Qualifications in footnotes, small print, links, notes, or other slides/pages.\n\nApply date-sensitive EU rules using the content\'s intended publication date. If no date is supplied, use the current date and state that assumption.\n\n## Output\n\nReturn:\n\n1. Scope, sources, assumed publication date, and applicable jurisdictions.\n2. Counts by overall risk and jurisdiction tag.\n3. One finding per claim and region, including exact quote, source location, finding code, risk, basis, reason, and remediation.\n4. Highest-priority fixes.\n5. Limitations, inaccessible evidence, and items requiring legal or technical review.\n\n## Guardrails\n\n- Do not describe `ANY` as a legal violation.\n- Do not declare legal compliance; state that no issue was detected under the checks performed.\n- Do not treat a keyword match alone as proof of greenwashing.\n- Do not invent or assume substantiation.\n- Do not ignore visual or contextual implications merely because extracted text appears qualified.\n- Do not apply withdrawn proposed legislation as enacted law.\n- Escalate high-risk claims for qualified legal review before publication.\n\n## Tone\n\nBe precise, evidence-led, constructive, and explicit about jurisdiction. Every Yellow or Red finding should include a practical remediation.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class GlobalGreenwashingClaimAuditorAgent(BasicAgent):
    def __init__(self):
        self.name = 'GlobalGreenwashingClaimAuditor'
        self.metadata = {
          "name": "GlobalGreenwashingClaimAuditor",
          "description": "Use this skill whenever the user asks to audit, scan, review, classify, or de-risk environmental, sustainability, climate, circularity, recycling, emissions, or green marketing claims in pasted conversational content, CSV files, XLSX workbooks, DOCX documents, PPTX presentations, or website URLs. Report universal vocabulary risks separately from Canadian (CA), European Union (EU), and United Kingdom (UK) legal and guidance findings.",
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
    #     echo '{"arg": "value"}' | python3 global_greenwashing_claim_auditor_agent.py
    #     python3 global_greenwashing_claim_auditor_agent.py '{"arg": "value"}'
    #     python3 global_greenwashing_claim_auditor_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(GlobalGreenwashingClaimAuditorAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(GlobalGreenwashingClaimAuditorAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
