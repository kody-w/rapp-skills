---
name: "eu-greenwashing-analysis"
description: "Use this skill whenever the user submits a product description, marketing text, catalog entry, packaging copy, or advertising claim and asks to check it for greenwashing, environmental claim compliance, sustainability wording risks, or alignment with EU Directive 2024/825 or the Green Claims Directive. Produces a structured per-claim findings report with risk levels, regulation references, and recommended corrections."
---

# EU Greenwashing Analysis

Run this procedure whenever a user submits a product description, marketing
text, or catalog entry for review against EU rules on environmental claims
(Directive 2024/825 amending 2005/29/EC, and the proposed Green Claims
Directive COM/2023/166).

The output is always a structured findings report: one block per flagged
claim plus a summary. Do not editorialize outside that structure.

---

## Step 1 — Extract all environmental claims

Read the full text and list every statement that references environmental
benefit, sustainability, ecological impact, or climate performance. Examples
include: "eco-friendly", "carbon neutral", "100% natural", "sustainable",
"green", "biodegradable", "zero emissions", "climate positive", "recycled",
"plastic-free", "low carbon", "environmentally safe".

If no such claims exist → output: **"No environmental claims detected — Out of Scope."** and stop.

---

## Step 2 — Assess each claim against EU greenwashing criteria

For each extracted claim, check ALL of the following:

1. **Vagueness / Generic claim** — Is the claim broad or unsubstantiated
   (e.g., "eco", "green", "sustainable") with no measurable indicator,
   certification, or evidence cited? → High risk flag.
2. **Incomplete life-cycle scope** — Does the claim highlight one phase of
   the product life cycle (e.g., recyclable packaging) while ignoring other
   high-impact phases (manufacturing, transport, end-of-life)? → Medium to
   High risk flag.
3. **Unverifiable / No third-party certification** — Is there no independent
   verification, recognized EU certification, or scientific reference to
   support the claim? → Medium to High risk flag.
4. **Misleading comparison** — Does the claim compare the product favorably
   against an irrelevant benchmark, obsolete product, or omit material
   information that would change the consumer's perception? → High risk flag.
5. **Carbon offset reliance** — Does the claim (e.g., "carbon neutral", "net
   zero") rely primarily on carbon offsetting schemes rather than actual
   emission reductions? If offsets are not independently verified under
   EU-recognized standards → Medium to High risk flag.
6. **Unsupported label or logo** — Does the product display an environmental
   label, badge, or logo that is not officially recognized in the EU, or
   whose criteria have not been verified? → High risk flag.
7. **Forward-looking claim presented as current** — Is a future commitment
   (e.g., "will be carbon neutral by 2030") presented in a way that implies
   a current state? → Medium risk flag.

---

## Step 3 — Assign a risk level per claim

- 🔴 **High** — Claim is clearly unsubstantiated, misleading, or likely
  non-compliant with EU Directive 2024/825 or the Green Claims Directive.
  Immediate corrective action required.
- 🟡 **Medium** — Claim is partially substantiated but lacks full
  verification, life-cycle scope, or specificity. Corrective action
  recommended before publication.
- 🟢 **Low** — Claim is specific and plausible but should be reviewed for
  formal certification before final catalog inclusion.

---

## Step 4 — Fill the standard findings template

For EACH flagged claim, output one block in this exact format:

---
**Product Claim:** [exact quote of the claim as it appears in the text]
**Risk Level:** 🔴 High / 🟡 Medium / 🟢 Low
**Regulation Reference:** [e.g., "EU Directive 2024/825, Art. 3 — Prohibition of misleading environmental claims" or "Green Claims Directive COM/2023/166, Art. 5 — Substantiation requirements"]
**Issue:** [1–2 sentences explaining what makes this claim problematic under EU regulation]
**Recommended Correction:** [suggested compliant rewrite or specific action the team should take, e.g., "Replace with a specific, verified figure: 'Made with 40% recycled ocean plastic, certified by [recognized body]'"]
---

---

## Step 5 — Summary assessment

After all per-claim blocks, output a summary in this format:

**Greenwashing Findings Summary**
- Total environmental claims reviewed: [N]
- 🔴 High risk: [N]
- 🟡 Medium risk: [N]
- 🟢 Low risk: [N]
- ✅ Compliant (no action needed): [N]
- **Overall compliance posture:** Compliant / Needs Review / Non-Compliant
- **Top priority action:** [single most urgent corrective step]

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `eu_greenwashing_analysis_agent.py` and embedded as the fenced Python below (sha256 508db0f553837574…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `eu_greenwashing_analysis_agent.py` first:

```bash
python3 eu_greenwashing_analysis_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 eu_greenwashing_analysis_agent.py   # or on stdin
python3 eu_greenwashing_analysis_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""EuGreenwashingAnalysis -- Use this skill whenever the user submits a product description, marketing text, catalog entry, packaging copy, or advertising claim and asks to check it for greenwashing, environmental claim compliance, sustainability wording risks, or alignment with EU Directive 2024/825 or the Green Claims Directive. Produces a structured per-claim findings report with risk levels, regulation references, and recommended corrections.

Generated by the rapp skill from eu-greenwashing-analysis. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# EU Greenwashing Analysis\n\nRun this procedure whenever a user submits a product description, marketing\ntext, or catalog entry for review against EU rules on environmental claims\n(Directive 2024/825 amending 2005/29/EC, and the proposed Green Claims\nDirective COM/2023/166).\n\nThe output is always a structured findings report: one block per flagged\nclaim plus a summary. Do not editorialize outside that structure.\n\n---\n\n## Step 1 — Extract all environmental claims\n\nRead the full text and list every statement that references environmental\nbenefit, sustainability, ecological impact, or climate performance. Examples\ninclude: "eco-friendly", "carbon neutral", "100% natural", "sustainable",\n"green", "biodegradable", "zero emissions", "climate positive", "recycled",\n"plastic-free", "low carbon", "environmentally safe".\n\nIf no such claims exist → output: **"No environmental claims detected — Out of Scope."** and stop.\n\n---\n\n## Step 2 — Assess each claim against EU greenwashing criteria\n\nFor each extracted claim, check ALL of the following:\n\n1. **Vagueness / Generic claim** — Is the claim broad or unsubstantiated\n   (e.g., "eco", "green", "sustainable") with no measurable indicator,\n   certification, or evidence cited? → High risk flag.\n2. **Incomplete life-cycle scope** — Does the claim highlight one phase of\n   the product life cycle (e.g., recyclable packaging) while ignoring other\n   high-impact phases (manufacturing, transport, end-of-life)? → Medium to\n   High risk flag.\n3. **Unverifiable / No third-party certification** — Is there no independent\n   verification, recognized EU certification, or scientific reference to\n   support the claim? → Medium to High risk flag.\n4. **Misleading comparison** — Does the claim compare the product favorably\n   against an irrelevant benchmark, obsolete product, or omit material\n   information that would change the consumer\'s perception? → High risk flag.\n5. **Carbon offset reliance** — Does the claim (e.g., "carbon neutral", "net\n   zero") rely primarily on carbon offsetting schemes rather than actual\n   emission reductions? If offsets are not independently verified under\n   EU-recognized standards → Medium to High risk flag.\n6. **Unsupported label or logo** — Does the product display an environmental\n   label, badge, or logo that is not officially recognized in the EU, or\n   whose criteria have not been verified? → High risk flag.\n7. **Forward-looking claim presented as current** — Is a future commitment\n   (e.g., "will be carbon neutral by 2030") presented in a way that implies\n   a current state? → Medium risk flag.\n\n---\n\n## Step 3 — Assign a risk level per claim\n\n- 🔴 **High** — Claim is clearly unsubstantiated, misleading, or likely\n  non-compliant with EU Directive 2024/825 or the Green Claims Directive.\n  Immediate corrective action required.\n- 🟡 **Medium** — Claim is partially substantiated but lacks full\n  verification, life-cycle scope, or specificity. Corrective action\n  recommended before publication.\n- 🟢 **Low** — Claim is specific and plausible but should be reviewed for\n  formal certification before final catalog inclusion.\n\n---\n\n## Step 4 — Fill the standard findings template\n\nFor EACH flagged claim, output one block in this exact format:\n\n---\n**Product Claim:** [exact quote of the claim as it appears in the text]\n**Risk Level:** 🔴 High / 🟡 Medium / 🟢 Low\n**Regulation Reference:** [e.g., "EU Directive 2024/825, Art. 3 — Prohibition of misleading environmental claims" or "Green Claims Directive COM/2023/166, Art. 5 — Substantiation requirements"]\n**Issue:** [1–2 sentences explaining what makes this claim problematic under EU regulation]\n**Recommended Correction:** [suggested compliant rewrite or specific action the team should take, e.g., "Replace with a specific, verified figure: \'Made with 40% recycled ocean plastic, certified by [recognized body]\'"]\n---\n\n---\n\n## Step 5 — Summary assessment\n\nAfter all per-claim blocks, output a summary in this format:\n\n**Greenwashing Findings Summary**\n- Total environmental claims reviewed: [N]\n- 🔴 High risk: [N]\n- 🟡 Medium risk: [N]\n- 🟢 Low risk: [N]\n- ✅ Compliant (no action needed): [N]\n- **Overall compliance posture:** Compliant / Needs Review / Non-Compliant\n- **Top priority action:** [single most urgent corrective step]'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class EuGreenwashingAnalysisAgent(BasicAgent):
    def __init__(self):
        self.name = 'EuGreenwashingAnalysis'
        self.metadata = {
          "name": "EuGreenwashingAnalysis",
          "description": "Use this skill whenever the user submits a product description, marketing text, catalog entry, packaging copy, or advertising claim and asks to check it for greenwashing, environmental claim compliance, sustainability wording risks, or alignment with EU Directive 2024/825 or the Green Claims Directive. Produces a structured per-claim findings report with risk levels, regulation references, and recommended corrections.",
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
    #     echo '{"arg": "value"}' | python3 eu_greenwashing_analysis_agent.py
    #     python3 eu_greenwashing_analysis_agent.py '{"arg": "value"}'
    #     python3 eu_greenwashing_analysis_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(EuGreenwashingAnalysisAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(EuGreenwashingAnalysisAgent().perform(**json.loads(_raw)))

# rci-capsule:v1:H4sIAAAAAAAC/6VaaW/jSJL9K4QHi+ku2RbFmwZmF7ovStR9dTUWPJKXeIlJSqQa8983kpRs2eUGdrH1oUqmMuN88SKCrr+etCx1ouTpLcx8//nJRNhI3Dh1o/Dp7WmNEZU6Lqbw0fV96uKgEJ1RAs8QlWH4gDM9cFNMaVScRGZmpNSDgGcq0JIjSt3QplKUp8+UoaWaH9kUCtOkeKZizThqNvnaiGL4OUoozQT5qYvLh77mBpQWmpSGj5hKI8pwkHGk3JSy4KidIBReNOzA2WcQeXaTKAxAtObfrhpREPuuFhroGSzFqeaGmu76blpQlygxiY7EBdGVZt+1y+vUxU0dqrumOm6CjNQ9I4qhGa4uMTw5R3zvE9VUmyjBH8deqVkZBETigdMEwpElyKRilLxUBlluSLRiKkFxlNw0ERMoH+LqgyEJsjNfI9GDjxZKEBgPj0kQQEsUgIEmiDSipFQahfj16fkJ5Rp4ivDT2x9/Pj+58PmeTzesDCEnIaH/IH71HwJHNUPNL7CLf4Y/w0UWVumGZBrIBOM/Uq793xL+M6wyDgH7lPQycwk6u+hCabZGzCMmJRlYT4HT36QRTPvtm1RoJBTEA4am+Toj17vtKk4kQWBcHGEI1GOmfoYfYtrqpA6i2HpDEH5/Jc6v4FqUpXGWUhABzb9oxZc8fsneG9iLKN2PAJKQYsryNdtG5s+wynXsZ+X9LICgFK9UJ6LCKKWQ6aZR4gLarqU+7JqkxrT0Q1NpzsvLC/nnH/+glimKqQb1M2PoBkd18zTRIOwa1OP3wYI8Iq0KgwUYKEuvDIzvQrBJMgvQpaWoBHup+gNqn2X+DHVIv+WmX+sH6s2IIKmuAYoBb2BRlWvfDUAyiQckOiCl9womV+j8GboQm8xEb9TPJ7j/YiUu5NAvfj49wxNDS3RAQIgy8NCvnjVo+j+oUIOo3J+82+EjeADePpU8UH2pu5GJ7EQzb1/DoytKIgoFLsakBG6a7lZG2CVoqJ4CNArDhwRWYmNfw6lrgJHodsCPLlRlZPXzp1D5EFTNgpNl9oYWJBtiZji3tFAoJ9GHJDZk5oazN+rHj59P0+jbPEJdpYBVgN0t8SoAM7KoJVAlIOTpx48ypziN4u/wwtyvNTFGGNRrd1Mey+6RQimo4hQBMomYHuSyvIIquBHKIZefbxTcVBRiTImxyIfAgIA3crHxCk5tNDsD3IDaOtWHD4lrVNfB6JtZQ1xerizSkwgACyqzEPgF8humLuQHSomiqN/Qq/36XCGmivtDwj+h4feKTyHwAdIwQAaeUqRmgYGi5LmUZpDuYpEnJV8RN89QgYBTygD3zf+6p2jg2jdqJnUNIWaIZ8Ow7CmQGqgmC72UiKEwycmHb50IPXrngCToLU5a8kXsaNBUI6u05kZVJY8SeVQl7+ZyBcjSi/dOCT46LnHLDoFFIGsRyEhKYUTPS1WLlRZM/QYVmFkaYZWySUIuQ0y4i/RL8yWyXojW39+dngA7ZQF02lLgLyFgSQjWITAIhLC0q04BfKFlJOZLrCXQVz/F92u6oZ9AciAjKCZtLExLNZW4e0ZIl7NDIEeTAPTXdGEDOKN89sFad4NxFpdt9T32vzr2q1MccWriYh9IsxpFIIRw4NH8LxmtjqBP6bO0c0QQV5SW3GtMCykXOjV0d8A0BWRqOKRFgic6jkoY3e6XvkXQWinCTKQ/lHLcsKTRch4omfoSZT7UoqOFdqXfAFbLApT8ExPSNVDZiP8exTzxtl0xbWRZGBHyr2akv3X3vQK/Y+gQVVkkPEtKEKQV4BQQbOLCJzhuPGorh0EMJBKAikQjoCCOhRQB6c3pO1uDLPM2uvwXBYxaSYCmWuIofQQSaKpgBLDJ4ElVEd31ywOcCK+YWmLi/wUohArpN0DBZShD5JMcQdOLvonU+zTkYmgcBUn8l04K9pRCnildM230fBdW5RVGDuISuOgabtlNHix3w1JHd00ulZIuDkw374xNOdq5ColOpp17JP4eBSJxDzj+AuF48aPo+DFuxwnCYDEiQzdlZADeMP1UxxpMFWRKIVUAeA3uZfyOkgtZFXREfUYLpRcwqbE0wciHDvBMo2DSugWBjOtkTiAVdFdezSpfK/nRm1+aH/vQ/IAoQdbHjF2OaqWr5UU4aUqsCX+bLAdBIaH6cLecG0lugJW1BJLypUHBwPtOHFVC3SOqKCCMwpf7/vH/WCmIqCFM/SbR9z72w33NuC0JpwwOm6+ffLFQg5BaGapvvCFUXYHskzeUDiOGD50Gl4MjUf2Zm7+2vIqQY2SQMzAVvlLtrwYSIY+Li46A0KBcMt2/if1qOQOWK9HlG7PvmsrBB6oswy7pQcRq7JS8CKirdgsyrVelUvKn/7mR3K2AgZ58ddtPyuEUVxb9Ainubk2PoJsk7E4nH2sBTNRgVYruA1S32R7ct4L7+HTbMD42B/e2csEKZ6SVtenbuwE/fsxuxFJG4Q2i8kd18pRFKbrPYLfBDpPVWItjwCq+kwaZ/v8kghakBBRSAm9lbB9gX/JD/TN8bnVW/5waSEwp62NLXdybcGXbjQO+hfoz1UzS14/qBNccV3dLMeDIRyl9v9g8EbT9fPq+UD4tdDdF/F3R8gPlDzVDpIPUMjhDjLPKg0Z5h2WokqGqlSiHtLohMexCaCrQjiXrl7xQcWYEQCRt2qi6T7nSvseoCv9DEbTft/dSJc4AIbicsd8JI0EXQu6PBXYv+SqrWnAHfQrmwDx3i/wCgbEwEpWMo71ffv7oj5ZrA32/Uf+caObtHAdb1n39oWD1h+51W3+e75VDareg/njoSnpkFn/+swzgrVi+1MxD/MsdGABKdpGqY/wMm1ZK3iv4/sMLkrIm8HuZvK/P72XyUCA/fnx6kdG7l+FNG+xWQCyriCDo2wXrzhRv1B/TP39pBe8989evH8rj7w6UlfL1W0akecj9PcW/wSx8S2mIEODi9/ezP36okC4Smo9XWGRbJX2XQOZDCAzgcBdDGZavVMg8Hr68f13JWkUxmchgX4ABXXvAHYQL+DMAuVSW2KTXPjQYAGT859PzE/A0CjG6v1AKtQA+P3Wzx+DfXyLBcegtcAIyi5/e/noi72EIfsirqb/+/fx0b1fVi6q0iImsSPdA5xN8TeiTZLg6XI4JyZmc/uupfANJPugCB3cGHB42qz/turDZF4xoFK2dKRVQyE5nr4dL9jALFotR1hpOMGpaB27YOx/6PX59pDfMfLlU1o3N+sQYjaA27xz9Y7/fX9b2ujjc8a1ZoQRsTY2ZJt2f7/bpkTUNXpZzfesKu6VGn6y1IOwWB1VgT0l9oq/zjbI5pTnP8dNJTV4eRo6jh7KaNvI5k8dqfcJsRgzHZLLeYNBYi2XLcxh249uu2fP06SG4aFrYk+exWZidpDWbr2rdlrY+nabDbayebdNOT5vBKWyHgsnYh/qWNk52vWGfOxfsa/6wsTjGVs2It92IVRPa6xbeIJZnXO/a4nW+SMe8sz3sDDrdbFZ9fxuiqDe0Nu1gE6SrIGl7yW59qLHNfnyahbSzKEJlH+iqd/J97hDLU1v0tmZ44ORZPVwx83PNC6f1iyDGx5jlJH2yqS9bPbp3mQ3y65hency1NjMntrYO+JOMwrGANfGat3tzVz9t25NVHLn0ZnOR6kaNpm1seoo9lphm1Dp47cPWNVUdNXbFYhyNUvmS96VgpPWVQaoc4xPtec1m3FgE7f6pt67n2Xw5ny9N0+us7VZeS8VI0Y5t09JaHNtL3e3Q9otZVFNX+XE+TFZx25tdsWzteoWcodVJyvazg2FGq912WG/E9cNsUWQ70SzQRVavR8HIdqvGYSQ5vVBvZdrUaS83tc1WnAu2CrAZKL3TNja2SnN68kfoNB4st4vZUsPxztP3m0Ls6XThj9JmLZy0VDypzdRVNpsEnMAv9rtld9seDVm5PYhaqbD05Vo92maDaLQ6KYu2ltPpejD2NsZF0uvdqd/gT+vFae3LA/2yX4+3vp0MjpYq9tJJI2qK01r/0pGb7Gm+HY+izW4tdB2VbSlrqXvpXQbDTZq3x9Iyobt1bSQc1OKqdVycX1B8FJvSdcxu8xZuLPkpamfm/rxehmIhz1Z0pzFPNu1BbWbZZ3lbLK7j5ahmhRrTvexWwS7vGI0ajYVlEl3Z62CYs7bpn7d9qbYIbFbY+tfU2a6LyFoNT81UuSTi4eDOZ9fdzmuMN13RR/bBTkLVdpXxMRBEHLdq3Nmv1+QzUmeqQYdSrZbSRj6PcRc35fX+uLJs5sjEl9p8IjLaFaG2b9cYdblqgjk1TmcZaWwKrDxDgRHp0ULttDBa8p3d/DifCDiyevZQytSwL6FZtp3nnSXTGvqA3utoEAhzZ1Rfr9fKAHf8ts62Ooy1RC13YXhgMxZ766mu2uH10kj38xbX2ra42elwOS5mMA7uk/W8pgR0k3NWxkjumutpOhZoiZuYHS7UOkbPZfedSbxkWbVDL46qMhWnzfpw4YbFVec2XYW7LpZoyQ6FhB/mq0zje2yvJ5ldNfOlYVvyr5wS+7vNsb5ijOa4N+BW8WSre8Yowld/QC8DxW2JehS4SXHtLlfDoZU7myWTe2p88ha1YWdwiQ7etpb7fQtHtXOH7k/ZFR/FjXlzv1mPsexe2FnSz2OpWIvWYnS15kauLbOJ6h2YYGZfV+eCWaQ1T2sBSPf97Xqg7ZTF2Z9MdWacnACxc2s97tSyrLtY2xbT7bINGRmttbyY4/2Vl69rbnbceoU4XRzEeG6Z5+G8dT5Zh466EY8S37ii/kZuc2jYtseKU190Gs3dNT+bXGfcsFg/CBrcxROufrfRN/L+tTeZ++C0sNcGvXy0R0UqCXteWTqHjtdw1lulfvDGfk9k5k1XGGX6JnPzlXZSTgrb6yfrTRrJ0qlQT4f9CB2KWLl6o6JwR1Nckw9RX21LYa7MslrNj/tawTTx0nUx0/Kd68V2JNHuXflp3OCPXF2Z25dkG24VWj0EWjBc59cGv9/vT8ploYjKujuOLv2JinpK0Br2PXdkXYbSdsWtLhvRUtrbxn60UvzJWbbogXQIzCJv2dZir8THeaetiP1e6kRsF3U9yXMHaMAIw/nlgrUxU8xdWZjnvZY3ENXWKDg0hh69KoZMqrtclm06et8VL/t9LrQbaWNA43wUsZ4n1jm2Uz/qansWyAt7u4lFk+HyzkFF0vKEDls/bW5awrXNxNJI4q/b1nbOtzd+g5WD617KBLmRrGZtPznj9lxWL2tzkaXDRT7Yhm3+ugulPBGPMjrJ+V52kit9HNcas9N2VfOHg+Vl0hZO2MlHB89p1etiA+hvoR6QV9BHZlJwQLlzfjPLbSdoO4NeVI+CXZbOFrmOUv8s6vUBjzml1/A2krhnxCbmRGecyTshz3Xr4GajemrW8eIwUuaid2hsp+E0UEJ5v5fbu759sKZKx1/TWF301O2VXvp1W9wkiwMaTIxB35z0LK1mz0/TWlZI/KlXS8/ubJuyC67PONnOm09NOkw6TU7x5Fa2mLSakZK5kmwnuwU0PEsbnAfbSc77lum5khLyhi07YbEbj7jrfOFPZ0ltUDdPyhgNRxnkqJebu4G4U+SdzKTDVFBnrq4nihuK9niR+LXOVQgNuS4oi2bXkwe9ldi7sjzWzY7MpbN0HfNn9xTH8+7Aml6TMz2SHZ7T+PpI469drXsxFXXEd2e7LTLy4cljw/x4HiWmrE7OC6ejy21n1mNXzuWUJKPmsj7ZYm/kdE5MczrYSPhwZA5MqLbEDc+q+eWcS9vBUdivYn3qzdRZLxFlvJfTyXlWr3ted85x0c5prt1DgGcHHMZr4ch1t9OIc2O7F7M2F4fdZtHanE/D09pcK05R66vjjJfa8lIWx2nHumbyQeub5tGyIqeLN9aO7uztfr8xwfK+Aa3fri1a9bUx2Oedk2f0Wp21wSY09CPTlOS8i4Jzm1uIk8lhaDLTvdxhm56OvBU/47GiH8TzxNt0+egsWfI55Yv+ZaWjkbET1lwm4SYriGNjN2N6DCvYNbY9Hah2rTuga6x47p9rvH6yJnRIT4YzPwkKs6sszfqRr6/imlST4ainhRcBn692ZrVksdbfWXVuo800e2bsEbPvrbULcwzrK+uKrHNz3glnlhg6WzmZTbN9U5hMlTHHCWlvKLlShw1mCW+1tNWAoTuaxG2Vdt4QopHXaE7GPdzD8lKwj5a2UFstrB6ukiONdpzKCy0yIv/rXzCVW66PbpP7cjxUlNfAhKfY0RhegGcmy+qyZUDHRLLO05ZE0ybLGJLF6QYt0QIniZzOs7rEMrJsIJFpCKIpmrIsNyzEiszTv8txPTqDElhVYLqHSV8z38qh/e1BoxGR3x6k1Rcv/6mRpeMJNoHEcMGMxitNrPIzG35A2cvjr6detI8dAxewnAT/DcLI2437ZpJq9u0X4KACV/+BASSCzH//D2MUWUTmIAAA
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
