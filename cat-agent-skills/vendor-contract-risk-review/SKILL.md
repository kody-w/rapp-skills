---
name: "vendor-contract-risk-review"
description: "Use this skill whenever a user shares a vendor contract, SOW, or supplier agreement draft and wants a first-pass risk review before it goes to legal, before recommending any change to contract terms."
---

Read the contract for the clauses that commonly cause problems later, flag
them clearly, and never present this as a substitute for legal review.

## Instructions

1. State the limit up front, in the first response: this is a first-pass
   flagging exercise to help the user prepare for legal review, not a legal
   opinion. It doesn't replace an actual lawyer or the organization's legal
   or procurement team.

2. Get the contract text (uploaded document or pasted text). If key sections
   are missing (no termination clause, no liability section at all), treat
   that absence itself as a finding, since a gap can matter as much as bad
   wording.

3. Read for the clauses that commonly cause disputes or unwelcome surprises:
   - **Auto-renewal**: does the contract renew automatically, and if so, how
     much notice is required to opt out, and by when?
   - **Termination**: can either party terminate for convenience, or only for
     cause? What notice period applies? Is there an early-termination fee?
   - **Liability caps**: is liability capped, and at what (fees paid, a fixed
     amount, uncapped)? Are there carve-outs (IP infringement, data breach,
     gross negligence) that remove the cap?
   - **Indemnification**: who indemnifies whom, and for what? Is it mutual or
     one-sided?
   - **Data and IP**: who owns data generated during the engagement? What
     happens to it on termination? Who owns work product or deliverables?
   - **SLA and remedies**: are there measurable service levels, and what
     happens if they're missed? Credits, termination right, or nothing
     stated?
   - **Pricing and escalation**: is pricing fixed for the term, or can it
     change? If it can escalate, is there a cap on the increase?
   - **Governing law and dispute resolution**: which jurisdiction, and is
     arbitration mandatory (which can limit the ability to litigate)?
   - **Assignment and subcontracting**: can the vendor assign the contract or
     subcontract the work without consent?

4. Report findings by risk level (high, medium, low) with the clause quoted
   or paraphrased, why it matters in plain terms, and what a more favorable
   version typically looks like, without drafting replacement legal language
   as if it were ready to use.

5. Distinguish "this is unusual or one-sided" from "this is definitely a
   problem." Some terms are standard for a given deal size or vendor
   relationship and aren't automatically red flags; say so when that's likely
   the case rather than flagging everything as equally risky.

6. Close with a short, prioritized list of what to raise with the vendor or
   legal team first, not a flat list of every clause found.

## Guardrails

- Never present findings as legal advice or a legal opinion. Every response
  should make clear this is preparation for a human legal or procurement
  review, not a substitute for it.
- Never draft final contract language for the user to send back to a vendor
  as if it were legally sound. Describe what a more favorable term typically
  looks like; leave actual drafting to legal counsel.
- Don't flag standard, unremarkable terms as high risk just to appear
  thorough. Over-flagging buries the findings that actually matter.
- If the contract involves a regulated area (data privacy, healthcare,
  financial services, government), say plainly that specialized legal review
  is needed beyond this general pass.

## Tone

Direct and risk-focused, like a procurement analyst doing triage before
handing off to counsel. Plain language over legal jargon wherever possible.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `vendor_contract_risk_review_agent.py` and embedded as the fenced Python below (sha256 a6d8eb8e80e0afec…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `vendor_contract_risk_review_agent.py` first:

```bash
python3 vendor_contract_risk_review_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 vendor_contract_risk_review_agent.py   # or on stdin
python3 vendor_contract_risk_review_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""VendorContractRiskReview -- Use this skill whenever a user shares a vendor contract, SOW, or supplier agreement draft and wants a first-pass risk review before it goes to legal, before recommending any change to contract terms.

Generated by the rapp skill from vendor-contract-risk-review. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = 'Read the contract for the clauses that commonly cause problems later, flag\nthem clearly, and never present this as a substitute for legal review.\n\n## Instructions\n\n1. State the limit up front, in the first response: this is a first-pass\n   flagging exercise to help the user prepare for legal review, not a legal\n   opinion. It doesn\'t replace an actual lawyer or the organization\'s legal\n   or procurement team.\n\n2. Get the contract text (uploaded document or pasted text). If key sections\n   are missing (no termination clause, no liability section at all), treat\n   that absence itself as a finding, since a gap can matter as much as bad\n   wording.\n\n3. Read for the clauses that commonly cause disputes or unwelcome surprises:\n   - **Auto-renewal**: does the contract renew automatically, and if so, how\n     much notice is required to opt out, and by when?\n   - **Termination**: can either party terminate for convenience, or only for\n     cause? What notice period applies? Is there an early-termination fee?\n   - **Liability caps**: is liability capped, and at what (fees paid, a fixed\n     amount, uncapped)? Are there carve-outs (IP infringement, data breach,\n     gross negligence) that remove the cap?\n   - **Indemnification**: who indemnifies whom, and for what? Is it mutual or\n     one-sided?\n   - **Data and IP**: who owns data generated during the engagement? What\n     happens to it on termination? Who owns work product or deliverables?\n   - **SLA and remedies**: are there measurable service levels, and what\n     happens if they\'re missed? Credits, termination right, or nothing\n     stated?\n   - **Pricing and escalation**: is pricing fixed for the term, or can it\n     change? If it can escalate, is there a cap on the increase?\n   - **Governing law and dispute resolution**: which jurisdiction, and is\n     arbitration mandatory (which can limit the ability to litigate)?\n   - **Assignment and subcontracting**: can the vendor assign the contract or\n     subcontract the work without consent?\n\n4. Report findings by risk level (high, medium, low) with the clause quoted\n   or paraphrased, why it matters in plain terms, and what a more favorable\n   version typically looks like, without drafting replacement legal language\n   as if it were ready to use.\n\n5. Distinguish "this is unusual or one-sided" from "this is definitely a\n   problem." Some terms are standard for a given deal size or vendor\n   relationship and aren\'t automatically red flags; say so when that\'s likely\n   the case rather than flagging everything as equally risky.\n\n6. Close with a short, prioritized list of what to raise with the vendor or\n   legal team first, not a flat list of every clause found.\n\n## Guardrails\n\n- Never present findings as legal advice or a legal opinion. Every response\n  should make clear this is preparation for a human legal or procurement\n  review, not a substitute for it.\n- Never draft final contract language for the user to send back to a vendor\n  as if it were legally sound. Describe what a more favorable term typically\n  looks like; leave actual drafting to legal counsel.\n- Don\'t flag standard, unremarkable terms as high risk just to appear\n  thorough. Over-flagging buries the findings that actually matter.\n- If the contract involves a regulated area (data privacy, healthcare,\n  financial services, government), say plainly that specialized legal review\n  is needed beyond this general pass.\n\n## Tone\n\nDirect and risk-focused, like a procurement analyst doing triage before\nhanding off to counsel. Plain language over legal jargon wherever possible.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class VendorContractRiskReviewAgent(BasicAgent):
    def __init__(self):
        self.name = 'VendorContractRiskReview'
        self.metadata = {
          "name": "VendorContractRiskReview",
          "description": "Use this skill whenever a user shares a vendor contract, SOW, or supplier agreement draft and wants a first-pass risk review before it goes to legal, before recommending any change to contract terms.",
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
    #     echo '{"arg": "value"}' | python3 vendor_contract_risk_review_agent.py
    #     python3 vendor_contract_risk_review_agent.py '{"arg": "value"}'
    #     python3 vendor_contract_risk_review_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(VendorContractRiskReviewAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(VendorContractRiskReviewAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
