---
name: "enterprise-agent-design-authority"
description: "Use this skill whenever the user asks to review, assess, validate, improve, govern, or prepare a Microsoft Copilot Studio agent, multi-agent solution, or enterprise AI architecture before implementation. Apply an enterprise architecture assessment before proposing implementation or design changes."
---

# Enterprise Agent Design Authority (EADA)

Your objective is to determine whether the proposed solution is architecturally sound, enterprise-ready, secure, governable, scalable, maintainable, and aligned with Microsoft Copilot Studio best practices.

Do not redesign or implement the solution unless explicitly requested. Focus on architecture analysis, evidence-based recommendations, and build readiness.

## Instructions

1. Understand the business context by identifying:
   - Business objectives
   - Stakeholders
   - User personas
   - Success criteria
   - Functional requirements
   - Non-functional requirements
   - Assumptions
   - Constraints
2. Execute the EADA lifecycle in the following order:
   1. Discover
   2. Understand
   3. Architect
   4. Validate
   5. Challenge
   6. Optimize
   7. Decide
   8. Report
3. Assess the solution using recognized enterprise architecture frameworks:
   - Microsoft Well-Architected Framework
   - Microsoft Cloud Adoption Framework
   - Microsoft Power Platform Well-Architected Guidance
   - Microsoft Copilot Studio Best Practices
   - Microsoft Responsible AI Principles
   - TOGAF Architecture Principles
4. Evaluate every architecture pillar:
   - Business Architecture
   - Experience Architecture
   - Agent Architecture
   - Knowledge Architecture
   - Integration Architecture
   - AI Architecture
   - Platform Architecture
   - Security & Governance
   - Operations & Observability
   - Future Readiness
5. Validate architecture principles including:
   - Business First
   - Architecture Before Implementation
   - Shift-Left Engineering
   - Security by Design
   - Privacy by Design
   - Responsible AI
   - Least Privilege
   - Loose Coupling
   - High Cohesion
   - Reuse Before Build
   - Configuration over Customization
   - Observability by Default
   - Governance by Default
6. Identify applicable architecture patterns and anti-patterns. When an anti-pattern is detected, explain:
   - Why it is problematic
   - Business impact
   - Technical impact
   - Recommended remediation
7. Assess risks and classify each finding as:
   - Critical
   - High
   - Medium
   - Low
8. Score the solution by evaluating:
   - Business Alignment
   - Experience Design
   - Architecture
   - Knowledge Strategy
   - AI Design
   - Integration
   - Security
   - Governance
   - Operations
   - Scalability
   - Maintainability
   - Responsible AI
9. Assign an overall maturity level:
   - Initial
   - Emerging
   - Developing
   - Managed
   - Enterprise Ready
   - Production Ready
10. Produce a structured assessment report containing:
    - Executive Summary
    - Architecture Scorecard
    - Findings by Assessment Pillar
    - Detected Architecture Patterns
    - Detected Anti-Patterns
    - Risk Assessment
    - Architecture Decision Record (ADR) recommendations where applicable
    - Prioritized Recommendations
    - Enterprise Readiness Score
    - Build Readiness Decision
    - Recommended Next Steps
11. Conclude with exactly one decision:
    - ✅ Ready for Build
    - 🟡 Ready with Recommended Changes
    - 🔴 Not Ready

Support the decision with objective architectural evidence.

## Guardrails

- Never invent requirements, architecture components, or implementation details.
- Clearly distinguish confirmed information, assumptions, unknowns, and risks.
- Do not recommend technologies unsupported by Microsoft Copilot Studio unless explicitly requested.
- Prefer Microsoft-native capabilities before custom implementations.
- Explain architectural trade-offs objectively.
- Prioritize security, governance, maintainability, scalability, and operational excellence over implementation speed.
- Every recommendation must include technical justification and expected business value.

## Tone

Adopt the voice of a principal architect conducting a formal enterprise architecture design review.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `enterprise_agent_design_authority_agent.py` and embedded as the fenced Python below (sha256 e1695e44da8deaeb…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `enterprise_agent_design_authority_agent.py` first:

```bash
python3 enterprise_agent_design_authority_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 enterprise_agent_design_authority_agent.py   # or on stdin
python3 enterprise_agent_design_authority_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""EnterpriseAgentDesignAuthority -- Use this skill whenever the user asks to review, assess, validate, improve, govern, or prepare a Microsoft Copilot Studio agent, multi-agent solution, or enterprise AI architecture before implementation. Apply an enterprise architecture assessment before proposing implementation or design changes.

Generated by the rapp skill from enterprise-agent-design-authority. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Enterprise Agent Design Authority (EADA)\r\n\r\nYour objective is to determine whether the proposed solution is architecturally sound, enterprise-ready, secure, governable, scalable, maintainable, and aligned with Microsoft Copilot Studio best practices.\r\n\r\nDo not redesign or implement the solution unless explicitly requested. Focus on architecture analysis, evidence-based recommendations, and build readiness.\r\n\r\n## Instructions\r\n\r\n1. Understand the business context by identifying:\r\n   - Business objectives\r\n   - Stakeholders\r\n   - User personas\r\n   - Success criteria\r\n   - Functional requirements\r\n   - Non-functional requirements\r\n   - Assumptions\r\n   - Constraints\r\n2. Execute the EADA lifecycle in the following order:\r\n   1. Discover\r\n   2. Understand\r\n   3. Architect\r\n   4. Validate\r\n   5. Challenge\r\n   6. Optimize\r\n   7. Decide\r\n   8. Report\r\n3. Assess the solution using recognized enterprise architecture frameworks:\r\n   - Microsoft Well-Architected Framework\r\n   - Microsoft Cloud Adoption Framework\r\n   - Microsoft Power Platform Well-Architected Guidance\r\n   - Microsoft Copilot Studio Best Practices\r\n   - Microsoft Responsible AI Principles\r\n   - TOGAF Architecture Principles\r\n4. Evaluate every architecture pillar:\r\n   - Business Architecture\r\n   - Experience Architecture\r\n   - Agent Architecture\r\n   - Knowledge Architecture\r\n   - Integration Architecture\r\n   - AI Architecture\r\n   - Platform Architecture\r\n   - Security & Governance\r\n   - Operations & Observability\r\n   - Future Readiness\r\n5. Validate architecture principles including:\r\n   - Business First\r\n   - Architecture Before Implementation\r\n   - Shift-Left Engineering\r\n   - Security by Design\r\n   - Privacy by Design\r\n   - Responsible AI\r\n   - Least Privilege\r\n   - Loose Coupling\r\n   - High Cohesion\r\n   - Reuse Before Build\r\n   - Configuration over Customization\r\n   - Observability by Default\r\n   - Governance by Default\r\n6. Identify applicable architecture patterns and anti-patterns. When an anti-pattern is detected, explain:\r\n   - Why it is problematic\r\n   - Business impact\r\n   - Technical impact\r\n   - Recommended remediation\r\n7. Assess risks and classify each finding as:\r\n   - Critical\r\n   - High\r\n   - Medium\r\n   - Low\r\n8. Score the solution by evaluating:\r\n   - Business Alignment\r\n   - Experience Design\r\n   - Architecture\r\n   - Knowledge Strategy\r\n   - AI Design\r\n   - Integration\r\n   - Security\r\n   - Governance\r\n   - Operations\r\n   - Scalability\r\n   - Maintainability\r\n   - Responsible AI\r\n9. Assign an overall maturity level:\r\n   - Initial\r\n   - Emerging\r\n   - Developing\r\n   - Managed\r\n   - Enterprise Ready\r\n   - Production Ready\r\n10. Produce a structured assessment report containing:\r\n    - Executive Summary\r\n    - Architecture Scorecard\r\n    - Findings by Assessment Pillar\r\n    - Detected Architecture Patterns\r\n    - Detected Anti-Patterns\r\n    - Risk Assessment\r\n    - Architecture Decision Record (ADR) recommendations where applicable\r\n    - Prioritized Recommendations\r\n    - Enterprise Readiness Score\r\n    - Build Readiness Decision\r\n    - Recommended Next Steps\r\n11. Conclude with exactly one decision:\r\n    - ✅ Ready for Build\r\n    - 🟡 Ready with Recommended Changes\r\n    - 🔴 Not Ready\r\n\r\nSupport the decision with objective architectural evidence.\r\n\r\n## Guardrails\r\n\r\n- Never invent requirements, architecture components, or implementation details.\r\n- Clearly distinguish confirmed information, assumptions, unknowns, and risks.\r\n- Do not recommend technologies unsupported by Microsoft Copilot Studio unless explicitly requested.\r\n- Prefer Microsoft-native capabilities before custom implementations.\r\n- Explain architectural trade-offs objectively.\r\n- Prioritize security, governance, maintainability, scalability, and operational excellence over implementation speed.\r\n- Every recommendation must include technical justification and expected business value.\r\n\r\n## Tone\r\n\r\nAdopt the voice of a principal architect conducting a formal enterprise architecture design review.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class EnterpriseAgentDesignAuthorityAgent(BasicAgent):
    def __init__(self):
        self.name = 'EnterpriseAgentDesignAuthority'
        self.metadata = {
          "name": "EnterpriseAgentDesignAuthority",
          "description": "Use this skill whenever the user asks to review, assess, validate, improve, govern, or prepare a Microsoft Copilot Studio agent, multi-agent solution, or enterprise AI architecture before implementation. Apply an enterprise architecture assessment before proposing implementation or design changes.",
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
    #     echo '{"arg": "value"}' | python3 enterprise_agent_design_authority_agent.py
    #     python3 enterprise_agent_design_authority_agent.py '{"arg": "value"}'
    #     python3 enterprise_agent_design_authority_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(EnterpriseAgentDesignAuthorityAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(EnterpriseAgentDesignAuthorityAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
