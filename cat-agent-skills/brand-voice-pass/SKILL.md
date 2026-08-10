---
name: "brand-voice-pass"
description: "Use this skill when the user asks to rewrite, humanise, de-AI, polish, localise, or align draft text to a brand voice, house style, named audience, or writing profile."
---

# Brand Voice Pass

Use this skill to transform draft copy into a defined brand or personal voice while preserving the user's meaning, evidence, terminology, and intent.

## Operating principles

1. **Preserve the truth.** Do not invent facts, proof points, dates, clients, figures, quotes, or outcomes.
2. **Preserve the argument.** Improve expression without changing the user's position unless they explicitly ask for a stronger or softer stance.
3. **Remove generic AI tells.** Avoid empty intensifiers, inflated claims, tidy-but-bland phrasing, excessive signposting, and repetitive short sentences.
4. **Use the requested variant of English.** Default to the user's language and regional spelling. If unspecified and the surrounding material uses UK English, use UK English.
5. **Respect the destination.** Adjust length, cadence, paragraphing, and directness for the intended channel.
6. **Keep it usable.** Return the rewritten copy first. Add notes only when useful.

## Inputs to look for

- Draft text or notes to rewrite.
- Brand or personal voice guidance.
- Audience, channel, objective, and desired length.
- Words or phrases to avoid.
- Required terminology, source facts, or claims that must remain intact.

If the user has not supplied a full voice guide, infer only light stylistic choices from the draft and clearly avoid claiming a detailed brand profile exists.

## Workflow

1. Read the full draft before editing.
2. Identify the core message, supporting evidence, and intended action.
3. Apply the voice rules without adding unsupported content.
4. Improve flow, transitions, sentence rhythm, and paragraph shape.
5. Remove generic AI phrasing and replace it with concrete, human language.
6. Check the output against the original for meaning drift.
7. Return the final copy in a copy-ready format.

## Default voice controls

Use these controls unless the user provides a different profile:

- Prefer concrete language over abstract positioning.
- Prefer lived-experience phrasing over consultancy jargon.
- Use natural paragraphing rather than long blocks or a list of fragments.
- Avoid repetitive, overly neat sentence structures.
- Avoid claims such as "game-changing", "revolutionary", "unlock", "seamless", "in today's fast-paced world", and similar filler unless they are in source text and must be retained.
- Keep the user's level of confidence: do not over-polish into corporate blandness.

## Output patterns

For a simple rewrite, output only:

```markdown
[Rewritten copy]
```

For a rewrite where useful issues were found, output:

```markdown
[Rewritten copy]

Notes:
- [Short note on any assumption, ambiguity, or retained risk.]
```


## References

This skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.

- `references/voice-profile-template.md` - use this when additional structure, examples, or checks are useful for the task.

## Quality checklist

Before responding, check:

- The rewritten text keeps the original meaning.
- No new evidence or claims have been invented.
- The copy sounds like a person, not a generic assistant.
- The requested language variant and channel fit are respected.
- The result is ready for the user to paste or publish.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `brand_voice_pass_agent.py` and embedded as the fenced Python below (sha256 e2ef6faf9fe6a576…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `brand_voice_pass_agent.py` first:

```bash
python3 brand_voice_pass_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 brand_voice_pass_agent.py   # or on stdin
python3 brand_voice_pass_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

````python  # rapp:deterministic
"""BrandVoicePass -- Use this skill when the user asks to rewrite, humanise, de-AI, polish, localise, or align draft text to a brand voice, house style, named audience, or writing profile.

Generated by the rapp skill from brand-voice-pass. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = '# Brand Voice Pass\n\nUse this skill to transform draft copy into a defined brand or personal voice while preserving the user\'s meaning, evidence, terminology, and intent.\n\n## Operating principles\n\n1. **Preserve the truth.** Do not invent facts, proof points, dates, clients, figures, quotes, or outcomes.\n2. **Preserve the argument.** Improve expression without changing the user\'s position unless they explicitly ask for a stronger or softer stance.\n3. **Remove generic AI tells.** Avoid empty intensifiers, inflated claims, tidy-but-bland phrasing, excessive signposting, and repetitive short sentences.\n4. **Use the requested variant of English.** Default to the user\'s language and regional spelling. If unspecified and the surrounding material uses UK English, use UK English.\n5. **Respect the destination.** Adjust length, cadence, paragraphing, and directness for the intended channel.\n6. **Keep it usable.** Return the rewritten copy first. Add notes only when useful.\n\n## Inputs to look for\n\n- Draft text or notes to rewrite.\n- Brand or personal voice guidance.\n- Audience, channel, objective, and desired length.\n- Words or phrases to avoid.\n- Required terminology, source facts, or claims that must remain intact.\n\nIf the user has not supplied a full voice guide, infer only light stylistic choices from the draft and clearly avoid claiming a detailed brand profile exists.\n\n## Workflow\n\n1. Read the full draft before editing.\n2. Identify the core message, supporting evidence, and intended action.\n3. Apply the voice rules without adding unsupported content.\n4. Improve flow, transitions, sentence rhythm, and paragraph shape.\n5. Remove generic AI phrasing and replace it with concrete, human language.\n6. Check the output against the original for meaning drift.\n7. Return the final copy in a copy-ready format.\n\n## Default voice controls\n\nUse these controls unless the user provides a different profile:\n\n- Prefer concrete language over abstract positioning.\n- Prefer lived-experience phrasing over consultancy jargon.\n- Use natural paragraphing rather than long blocks or a list of fragments.\n- Avoid repetitive, overly neat sentence structures.\n- Avoid claims such as "game-changing", "revolutionary", "unlock", "seamless", "in today\'s fast-paced world", and similar filler unless they are in source text and must be retained.\n- Keep the user\'s level of confidence: do not over-polish into corporate blandness.\n\n## Output patterns\n\nFor a simple rewrite, output only:\n\n```markdown\n[Rewritten copy]\n```\n\nFor a rewrite where useful issues were found, output:\n\n```markdown\n[Rewritten copy]\n\nNotes:\n- [Short note on any assumption, ambiguity, or retained risk.]\n```\n\n\n## References\n\nThis skill includes supporting reference material. Read the relevant reference file when the task needs additional structure, rubric detail, examples, or checklist support.\n\n- `references/voice-profile-template.md` - use this when additional structure, examples, or checks are useful for the task.\n\n## Quality checklist\n\nBefore responding, check:\n\n- The rewritten text keeps the original meaning.\n- No new evidence or claims have been invented.\n- The copy sounds like a person, not a generic assistant.\n- The requested language variant and channel fit are respected.\n- The result is ready for the user to paste or publish.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class BrandVoicePassAgent(BasicAgent):
    def __init__(self):
        self.name = 'BrandVoicePass'
        self.metadata = {
          "name": "BrandVoicePass",
          "description": "Use this skill when the user asks to rewrite, humanise, de-AI, polish, localise, or align draft text to a brand voice, house style, named audience, or writing profile.",
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
    #     echo '{"arg": "value"}' | python3 brand_voice_pass_agent.py
    #     python3 brand_voice_pass_agent.py '{"arg": "value"}'
    #     python3 brand_voice_pass_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(BrandVoicePassAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(BrandVoicePassAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
````

<!-- toaster:generated:end -->

<!-- rci-capsule:v1:H4sIAAAAAAAC/41715LkyJLdr5T1PpBcdA+0GjPSLBNAKiRUAgm1s7YXWiS0Bq7tvzOQVd0zl7tcsl66EIjwiHA/fvx4G+rv37xxSOvu2+/VWBTfv4VRH3RZM2R19e33b88++hjSrP/oX1lRfMxpVIHn6GPso+7D61/9x1B/dNHcZUP0/SMdS6/KevBbGP04XL9/NHWR9en3j6IOvOL9ogbLiiypPsLOi4ePIVqG3YT34XdeFX5MdRbshmqwwUc/rAV4qLwyCj+8McyiKvg0se+XVclH09VxVkS/ffv+LVq8simi/tvv//Kv379l4Pdvv//9W1B4PRj6dtytm7txFQwckqgawJrCqxLwslmBAyrw3ERdXHclGAqj+OPr6b/3URF///jnf37NXpf0/+P3j49/Akf2+iHqfgeGos4bovDH1+w/qo+vny4axq76yPu6+i0cy6b/73//41s/eMPY//Ht948/vtWvP759B/9mVT90Y7B7/P3mKuvG48kZV0XWv/9p7z/52dc24/Be9Xm6/9f8qh6iz93Vru6jH3VVrB+B13h+VmTD+vtHXBdFPf/DGcDk/9Lqn9bnbEjf8EiyCQDl83C//fHt37+D30Pg8/+J/Q/w8A83Bs7+p493eD7e8fnYA/RH9Uf1f0APgGQAs/rdyV/gCepmBYbf8AEByyoAk08YAYiAeADPe8UnpAByAU4AXiIA3GmHzk8U/7f+o4wAaqvk+0c0ZeEnxkBsy6yqizpZv3/sFsE24Py/7Qf7p3/6UJo96p8IzKog24G3v0J/AzhRPzeJ3luAew7pb//8zx98/QGcD+wAzwwfsRcM/fcdvzUAWg2sg6cQAAn8ExQA6PtznCVjt4+0Y/1+A65Vj0NQlxHwaoX9h80AAsZyPybY71oC42A8WvZL98DVH3t4wPqPIAW4/z980NR9tsfjY6zAXfr91bqvLbIgGwBGQK4DbIDkBVnZ1VUC0h889XUMPAWGPOA1cCR8P9IjKveN36mRBR+HK/BmUfT7oQ4gGOFHVDbD+unRPoszEKgdH3Gx5xG4vZeVYGDIwvWHPw4//GL3f5N2Xv8ZpCXY7wN26AGPgHMP7+F9Uhc10QCusb8DlDZ89NG+SfB2F7Gf7RNUEZjZjlG/7zd5XeaBiIA4CFWy09U7WlHsjcWbmv7ipJ0vRi+JvjZLsjfA+gZcD5zht49rDNwHHoP9VuF71r66H7uuHqtwd3kJLgk2LHaT/cdT/Lnp933gL8/gwOSnM3d7w9sOoGZwV28P09uZYT72w0cRVckA1gfeF3Ybr/OSzmvSX34Jsw7YqPa47jHcbb29H+7+BmCoogLsR+37iVHUfGQDOI3nA2IF2zw+eezTazvxgoWfqRdnXT/8Bs4R7tAG13mzybtGgMvEY/EzXa5vItidWdT1G0f7ix8f/J81ABzr08af9eS3fcrx/5LPyZiFX6D78XH4VRu+bgNSxc/BlQESvjwQ9cAH4Zez3ousugv7t+UdWp87ezs+328fACDvFf/ABH09dmDzr+wFaz/RCpzjDR/lHo0uKr1sp74BzHnfH4DiV8VMvf7NAv3YgMzaIfIB3PTXO0XvVNiza/clqJTp8K6DGQh9AK63TwRR7OryExJvD+43DIrI6/ZEfafY+1w73nZmHDzAfT+p8atkgjQCJvufEQLOeMWA+L9I7BF5n9B9n+5zEz8CcQPrwnfp/eSf607qWby+5wb7a0BNPciQ7+8rghTcz/Anrf5i0h153rsAfLLGAfjj08qnK7oRsNAvwvLCd+6A3Po0usO2/knIIK9/ct1+g++fZeJNZiBGPxngo0tBlS8/j/ArQwBNeE30mWv/kbZ+cs5Pbik8YAfkxrvMgQMEoMT/VD2/uOEzkbg0Cl7v+4DzN/sVEm+vep9DXQboF0B5T8av4gOcnMX7dejf/ppx8XveV6EDwdx/+9GB6Kz7YkAmPwP4k7A+3bd7p6uLv9RRUCV+jf6F4z9huXsPhKjf0ZLFAH17ifoCyu+fqQrqzI7Kn7f+kwqBz0BV8EFVAPH8VUY+EfJrWQESMfwByglw7Tsav1z7Xg6s9uDwIJ/XjxwUsTcqfnzsJwd0N3bABX8ltQ9Qe9No57Hd76AYffhAYL7eyex97Kmys3kMFuzFsP+kiHda/Fkgvr93BpirIu/POvHxqUv2qvuXVV9J3o9BCuog0DkJUKQ/flbRTxHXRVNdjPvVvW79HAJeBqf6/L2PvHL3+U/FB8gm9FZQUmKgI380AFjhx1x3RbhP2OHWg/QtvA4AoCjAVf9alb1up++fXPRmz33Fm378naRBvgMp9L7Am87/WsGiKSp27wCXx59Z+ftH+ClNdof8+FTsn6oKJDTINlCwPt41eK8fvwTQJ6obD1SDrnrj7PSpDnblHf3ZEnzBf2ezN5L+9re/lV73CusZPPzL4x8Kyr++X/9p68vIXlG66KukfGR9P+7UsA/Fe1X9ucf/j/k/KnkvMr/vrvkX/S0R9qoDjgdcuIucHgj1PYggCKUP5BfQxG+e/+nUjy7rX7/9edC3Mx7RO2WCTw1o/KlZgTQsxj2v/kKG3c/Jv6TAX+i2i0CAdjXy56w3Wf/qu4Zdh1VRBCrXTorDlwL5idrvgDj9nb0+SX8XS59d0Wex2knpnR5f5/ntM7f/9mu3Hn7zx4+v3P8xAKm2y7LfyvBvHz/eEuUtyd/n+c8P8B937N+I/QrfT/2xX+QnmLTR25uPP8+3jx8/yw3IxKZ+S6fvn++/+Mj4BznyToIXwHr/jwT7Ra7vVJAByqP5VzH6S/VOPcD7fvTuWHZ1/pU7xrumAebtd5iB3MleQPl9CZHv75TxfpULAJ1sl8HDb3+e7qfE/MWVP7Xmu15/KhUQ3+Htn+5T6P1lbzCyMzpw9y/C/5OyQXo2ewv6FjCj/5aMe0cLolf10c9mfm+d/0P3uze6gE1LQONdvzfJINrgUkO2N89/B+1Z96V9PlvpYW12G5+Cau/edkR8tsn75K+Wap/992/eu7EGv/gUAdZciP56+PzhYNYkdDfKV/leqBV1MgY9E+tReh0T4Tl5zdGtNe11u2r18UmTSH8so+jiHrUwxvHwFSzuYNI2HK0OKTSzjAe4vI2DNUGQmhBigD8R/3441vXNieCmtSOhPsXkIdqO4jXP8f55Ee36PD1ari9jjlO9tjtFnL4UT+I8qd0ibbzOU6RzqOxp81ZaIhKVtu1mc91hYVeZQxSV16tC8fzB6ua7zd36NUrDeJTtdHG5lOfgR4IGfn01ngahGhKWFAdvYGVCtThUmQo3cs6SnULR8XjgXu2mJcowTMosqyqzWCO+3UQa9mIFLhQlnOLgyZ5r2DR6zHIUasmRTWx972yaaeBWdIXnGE94z8Y5JjKKD4hT9tt9TgZdgtF4ytd6c2IrGDaE1pdBMysoiaRDq8EwkiQN+SSEKuDtgZqqhYkv6fWZr524UNdg01GWKSIVOVlwPj9v9jAQQQSNUyDnmGZOvCuVpySGmCjKIP4GJ2bOMkwi9jLTgjRN4dJ1SxPHW7bCm6LyHEIfxjxKjxWDj1qyPKyrdKq4ddxoR+h6ZRIHlYcQ2M2GHg6xypME6MhmARmVqV0OLCVdbhzboITeCKdsGRIxK0ctHtFjKBAEd7Ju4TC4s80owWWKJ0o9onE8TchBG+GAh5+48qx0i/NSaaE2iZ4u94EOXYhj55E8xzZ0hX3l6cZQx6I1TgSh1yExMzPwcysnnGKgszFurxr3FsnuNpYN49ppAMKkMy0UD7SMnYj0Zvr1SF6isB0im2b8Qx+KWoeHy2wVShuuNoOlB3WOrNaMPWi9q8QUwCTTyXWgXuhO9RvUK8JjkZMQHPO0BcHqhNiJoAVSbJd3IoxgHhcOg9QnMX1ZRMtXL20KQYZ2uMc5QT4giTx7N4DnJFXZnmBUvKMRGIa7FUUZld9YtBT0ZKhPRrFmpNNJJzIMoqQxC/N1WtNZO4O4t0jvEZuAdNlVEhsPqS+swQZeK1pwecgnv6rwOqziJ6WOQ6pNgw21MHJEbjx6VXXZsYnpxNRrQGhFrSDX1UR44SwqnrWl1+TSaC53n8T+utyFlEzCoH6gT95xvBYOIBGKr896FBh18mYGSWylunePML31/dZtmDdD/kMZk+FSnasJR54Y5DszRQvoqGHJRWx7smHSoqjtW3y0H515NkMogGB4aH1XyyzxID1Y/dgGx8tKnIJAez7iyPF6cNhnQPBQD0mHUGJHQn4WcaE+rTg40frYidtwPwh69LywPn824dyX/I4IiKbftAjnTyPh1Ae8tWvhxuTavSqpCncWfuUPDmHgDZrlviHpSVkZs0KLnGihCx9lxMjV6XXNNvR5Ko7GdtyeXkL5nXBk6uqsAlwnRYxJsnQJa8Z+Gnl+PotTdNECI2FeUWhH2lzzMnK8sI8nO9on+5Ry+VErqKdmKhBmmKgrmcSsXuGH+LAvoZgJxiMdDqIgPyvyEptT4PF6w/FcifAxLNF17zoPik4j/uIM+ODVXs1nabuoaDtJwXR4CBHHl0BHdokU9sHJvivKSN5x6dldTx57plVqLdMQUTR3G3j4tVxkNTxdGERU5AEykXqrn+g17yjWOGpPWLsPZ1HynVuExE0YAgKXrIsLGQtzJGVfYSMm5SLEcuVYIEP5hs1p8ZyObWHXcYlBrsie79eobSfIwrigFjTsWa0zdOSWTqcZPiEIvQ6eyzlhTy1THVw+T4qUt8/bLE09nYU4D+QLVVbppVrGZytqmbqsAX5OaMtp9OYhxR6v1Ic7wz1e2zaONaLflsLW7ymPQCzmj4R2pkPfn++FFTCueo2vCm4msaKHT4aFXygCKP2cBE8Rcd2H2C3CQTg8D1BQWDLyUvU+xE7VebTNGAu0G1bhQKlujVttoNEPoIgRprIaVHPRgkao9fhYF/qJH5bxcrKS2/TEjbhx02muiYtzQ3JPEZ5jND7ZDTvySe/YeWbp1ztp6tF8qAxEHurokuQxF/tKameXMNkkIVPQGc2rE0PgxpUysyifAJXFwzHnBON6sxHmetTllYC2VStl2uG7SRxbKDvYQKedSKONGzqZX3Wjd4cpGElrY84uANkhJ7ESeTgPnmYEqvfRVZQYuF8HKJSr5JnToxmtqdioRnLGLNeogzAVMfrprhim98UV4+A+xaM5DOkmyh3+hj/E2Ub0DhpgxRjndOAEAXIUP83pCGLYZ011kKaXTKLMiYtx25DUcAeJbRyPiqA04kulxdzn4Su8oNOsvAo8hq1Mz/t5arT4pBiHJZzSKmeybcTPU6hR4S0nUFS5gTueXsvZnY50ImJqOLPxbVw36Ck0j8pOaYi4vGisvNVEpHDKrefM9Rn76XXSDXHYhufTs49WXFIUHrQP/sS7wZmr3IVpVxXnL6V/yqREeaXxdTni2gVRfSMIraetX4roARReJg1usfhYp9mGrTur2lw97zhqFJkLQYjqcpT6rS1ele3sqNpsG6PTl7cb0tJrliWMSacx6KKdZb0ndhlRlwPqYZiILjhQGtTBKHv/wZjzQOXpYjwQrHeXoG2PAmKheB67Q5Wd1vywcheGm6/bHFzOEyvczKbIhy57jmLiaxqiPAuO1VH/vI0SK60nzrdWa7xhN0QjYLNUtkXcWP0lhF50dS/R4JS3/rHdhCs1baOlLgapXeXscno+xTxUlhZm3ZUWpfMxurd4cgmPqcNJz6sjmh7TTV06TkIZR5tf3dqac8OuQKHryG3NAodkPrUa63bCmMA0QRCwcOekaqS4Cw5HMRB88MjA01BQEiE0etKEOpL0SccLBagHY9d6kwdvcamytjiqGZPgF3IK+WZG5+F5GQnbES96278QoqpR+XrndOYF1CukImjbIWsiX7aRkkNJ9ZKEaFgTh9sRXU51zo2SS0CvM08qUyofqjXBHmJyYK4reUGfD/Y25fZ6OpqJeBAbpzys3Qmyl7JFY8E6eeXdHt0ra77qSiUo8+oY99ZRL9kGSyGCQ0yn+fR9wfFLLKvtMRb7B0kbzQw/j7I7Ud2yNSwcjvwkMtfRNSGFRk2cuGLMbVBGuTqpjELEcQ6RxVIKM791N1m1ITiwL8UVXt2DcnycxHDKXOvEXodA4fL7NbBlSkQA/dLueKVX5ICkYQgnV9BrDkV2EVIjV4RKP3LZyJ6SyzZczwpUaOVTSS7WxNogzaIJm0T5irInt4gqeq5PlQWbixcxHD2rHiXhpVQ8RhkIswZrBWPZHkc8lKe7R7VGttFJgZGOIt4nrhSPK3qvhjC54z6Cu9EWnbODcDxO5wNuPJUQs8ngxFdcScvxBOMzkELrjPPNMlZ026UFHPopGY0sxtrcEaIIh8UPBgsPk7/NONtCG4QtHiMzGmTbBBNbbB0r4/0CI+y4GPREmDIPT0VGKIhH6OR42SCcIeDrpe9AlPlwu7MQdGoh7tQh/APvISKCLxMNpKcgiBcgAKcFKwfURNQhXNSBRcQgh+D7zPBwuEU83UZEyTdGPMkRPYuRjWgMjN+mBKPD6rgJG6zY6mPW17b2Q7qVacnHDJ50SUrBLx5hwTYuM7xgaLIu1+uAVfBGOOZcMk1xKwV+QctpDtWB0eSz9FIMZsCrifFnP+YvgSeAopAy2vWW8T2qqrmN5pCDXtgzYWVn63ggnBSGWZqm/Tgi4Hga7xUBT/jCt2usFNJB1iy2glnmcZuOVe6W9lW9TDg9whELDD+mYrjjtLpFbhTisRhSE3VktqFXzYm+9DE0LypssGJQxcKEXepzHGWHG101RBjmQAzRXYNNN5pMeOcwxqDvk2lIxyPWz8pbEr5wAo8XmBmJ6Y7Hfq6weBKRVVvMwOcIIwDRRLJRN65EVMdQKSXHFBrlC2M3tU1KAzv7PR8J/HSC5rA7cWbUu89cX7PqsK022LTkYQgK47xYGAYqA9zuLytFQeGCn0plOtiT4tjkAcvY4apUBTlONIOS96A4ICC98niQIMO9nKl72CGRPssm40F+i6re9tSi8eSBEtoVCIeWVzsyj0R/Uhe6xYuTTvh2/LpWlaZcJdBKYDf0FBVnsXta7iBy9TI2x6X3YJPKu+i+rWhvHgt7s7nkYXTCHe2OYu76pzqQCGK5TTd5GmnAZ+o97YtVTO9kXKGZIsD1faZZ3pieBkpoef8o9Sm4NOeLPVtUh6q2U7VscstwKsAHaqQeWXAbRxOqPa+XsLHK8ERiE8qNA3FAAsgZ0g13zGr2s2est5Z37+JuZP2IWy+drTM5P1/9pOfs0GV1CNev9ShBCz5RDEKwwy2wWAm0ra8nraUEXFx7vXXPIyU9Xz0aFfQ4UBXHjWSyarmhkWOG3Bi8mNcnCS/rg78JI2MX3mPt769nW/YDGfYvyYmI09mG09dyivOVskmDUDQgLG0ZJUhQ/CNySuObc8AKAa6m2YzYLSbLdsPPpIJaJkYkROu4SO9XMxvI6tAX5Sw8s/G8vZqUON2F+fHoJ1qUu+0ke4BfFfUsL0N0gp2xYZrXWD94wliuiXcoUPIlRiYQinJlkvHor9BDsJ4tioOWW74b6Zh2G1TctReqaTddYgSZuyVkAfujiRn1go84tzkWu4zFcO0ZY8U8BZPIiiLuIetvg6/rsWbX3ILDatdvpV7JHNXKykO94iqJP3g9VVhChDooWillnVYo1x/yBW4NrT2fBAp1g00I7RaCzmKAjcXhDHO2505xNqByelclK6oWzdg4FciCokeBhMMrD3MW5Tx79qYrL+n1DDSero18ezKUz8802Xa+McsTb9yAWrq0GDq4Qvlc1ZxnDaPoU+4s36Qr+mqHUuxb7HWVhx5jBbJDB8572YkL2rvSm7JV93GXgpbbnXqwNVJtsjQr4IC6kXJie2bt262ec8433FaVcJL0GBxYyJvcd0JJQUdQyAhdlxcQyrvdmLZFouUZspPuinQyU4D4CoqMuEE5LUdism9OBWrntch5WrWU7Ybd+as1os16RAEcDTAhwmKkTMfNjmZfngrfOo/nMg1gQdN9mzwb82XFNmpI2y3dTOPGEadkqwFtPyh9XCQUE2jnUQd4kNcOyzG2XjeVw5exh4+Nard0wJsOruSbuv/HxCwVerK1T1CcqJI7YzR9GHHvYQux1psqcJ33jKtiRM2BlC/eWAMYRPg5cLWB7bETVrJZyKgLR+jwPRlijL9M4eV6C1BcZ6XxcUCLO6dISFkm+pUztYu0Qkiha8JyuLVkzcWP4DkLk+ZK5EsiqUiWAtqkCOL5qLXgvjYpaHU4h4p8FC6sSjETBPjKh/IzYO4y5RQW2OfPC2i9HX1r6r7uO/OAEePjRGzkZjnt7Ely6BXqsVR99Ywpx5GJltlcQ/MopycFOls4ET8PPa1JrBPd2itk6qgBP2XTIL2zs5GUgMlwy0kJihwoo1IfgeeSavGiCnVAXEwYIkxdxdfgO44P4PUsbxHzgl03WOoMldLNQNMuWrnB5jVQo7FOwXPovl7g6AW52st5YcNiuMMj2ratWYXrwwblL9GV7plBx8ZnKvVactsheuCI0SjD8JDujXsuKGbgcL9bEym/O0AcZo+U4rWNS6DsMuWFoQtYfNMz/HY/pVZ8VFVzfJpjGkPblTHINKPEMOxRAmGnqeW9C5Vbgl9edKhKBcS5GV5c5Ube5xeMqO6uNZRyTmBZ4IddkyfzjeTumtVjHJpLZ67bsMCqX4dpoGVc9CIhyuNThF6qVDneCScP/DET0Tt1NccTaWE2cXfRYCIrW+SygFLMRUQJiSXCxNvunp/rtWlESWERId4Np9dYuuasSXv3M3VDNON1YqdZoJwhGRvz0/I8k6AdwPtI6iceOc+ndjr3kHfISxr0lYh6OR82hF3J08kNX+ZQmM5h84gJC6SXbuGqbsJiqgwUhXYeS99OcI/yz4GIT5NyH5BBDnCjI0fYKedYSy4CFvJxej0x0sv17vk8SGFTtCFaKSRoYdzbg2fC+70iYbl5dDImYs7wcu/2FWvyUZRy0Y1yd7lCpwdSSTZz6LqROia6YdgopNwlZNOfDqXXBeE87KRaex09pVwplBBM30ruua2gR3jisndSyVItDyUDy+RVGJHZ6I28SewnZj2VE3fvnvJNmNBwOLK3Cx+R9qHsRvN4CefMS7tWmmETGay+dHz6pfnkRSTtirtfGwxbTbh9wQY3pFI6UA7vS0tjITZJXuNXtQXbeREQSL2yZzGWiSfK6HU5dfyUBibEjkNwLsr2HOusd/Up7IGelKQorYk05dw99aASHzfTT2+xabkxNknhlcSEW26hDFkzwqVts57kMC5/AHkenE6MeTUtqhq7G0rmD+ti0qhjIE7vR+wje55eUl/EqtMfW73RwvNoNhHnmOMy3pVNpKho67pbcBaaoyGI2AvB84ZNyYxiirQ1cAI+Inp5Px9nHTIM7GFV0y2P0iFevGfhzU9d9nthuUuOJ9n3cAjqAkXGCATwPtk81dJnvJPYMg0fWhCZgUPJL1OUZLLGDmq/1VfsIg4nuTuTxEzgdyPq6YHo/TU6er2FyewrOW3Ws7C9QR5Pdo20TcHUBDrMeelo1Dg4NCWRNw/KyjB/sIdqbBY5PVTVSBOrXfDKSVjR9SEWGCLMQ5DYj8pCUpN+3M8M3aS1XcKFzpFicn/6hXJDpvY8JFAo9JW0OXHODi7rBnhqYYZ7GGXsThfi2rNM7XBqx+kYfbHN+zXk0nupZ5V5KfK0GG8BXfiRn64OnbuJW+DnxWus2HULCx2P3PPZrsITiOy2wDB9E5w8CRFKuDXsK60RYhAll7u4AtVjpTM3c4HILrXIBe/wmbutV3YKFN1N7ysC2sumVJK68TAdTSEpObNaVrhhSRvqufOu54zWE6YpYfs5FXn74sWKUzKht7uuROOTuVjnqTYL5xpAwpXTBERK8KdGa7MXUChf1zN3Jay7qjZoLXUCp13wR8+99CpcpdIRgJolT5uS6PJV4gexJc8Nnd3uueOmz0Uqt3NcbjHnwqMYGEXL385pKdKRZrsH/saj5uWRGdR6JWzdQ2cd7thz+gjc2rUMc6Io32tOm16VDH/DZiF85R3PgbPen3SeXO7+xU7DK2IdkDY3TaNWr9ZrKPqKn+ehcHz+iqi08ch4q51JcpvJSn6AukINlqXPheQdMOzVnoQ+v0mwcXwA6mSvgWjP6M2S6fWQgg7ZKhHiFL8QFZs5f6zak71QD8Wnu9Z5nQmOmM7IKzXPjPuMPd8txztFiovpClVyFgi+4Tflwo2KvygtUPxHmVdVpNZ7HUYYmWoZzlteeM4Hhm8OQ+q8HBv2Wngq7/fecF/9oFVR2yHUI+KsXPI4R75odQ7fKb051829hpPT7U5fktqF+USnevmVnZkIdfRjvXWPMqlB6ldnhjyIpfjCHefYWslLNdO4LbRDeFEkzEqIax91zuPZJHeDx/l1bSG3ZARtvV3NuXGVGRleLx9Hcucls2OIDLQyzx6aZoCJeO3QmxpxuTEvvVDPXKFFsmOejHsYESGEmPIDHuaw0ILRsvNnd8Fufq+O4ZgYCNN5YxZsR8QMzife6luxPGIEGTdnG+j7ykiNhNRBlq+YEb5OviFeDlQR5zfRMn0L4ZH4dG4pJa8mnxIbAWPcx2s+zQVwbXJ99Xi7MOuzva/8Y6SlcqFwtG5Nr9gyLO3Km672ozzIpxvEuMtpmzxPeYilrwaXvllOGdUHRYRq9+xlPnN6Sn3KvjDI83ngWdlKnAnpTIrLel3Q7s5TVPRadDuCY9C+uECzebtGNPywngutl0UwXaVbh+hnmroaSFigc9KERwNaUdi7Zldc8fvSRUVYtx9mNy0n8zb6pyudLJrdto5QvDTH5mfmTlHpaLA6qq5eosrtpGnneV4rSK+pYLCHMmMPoah3+P0YBl2P8VRgnlz6Xl8gHm1apSkX0Vx7u+EOrMc/71WML1Z/Lu7d0cB1+2pp290qXnFA3qJzqRNKlne3e+FpcIPo1gM0H96x17D0NlwuSJoozoDox8ZwKHVw8PR4806y0YjhFhXmcgb1X8ubOIcE8WklWy71jEt6OeEvE+01hh0gWAkpVnXoqppUaIkcyyy1XqSgU0jcaYKkcAN2Zj3pJSEBRpo3jZyBMircTZFX1L2NaJIbzRF+cjHvH9LcKFn+4a2vI2JAxWrJjyQ92rfryB+2Fsqs1udIIXekpuvlBzahykDeE/8aHp5xSOveqTInmjEXDjddeRWl/spn54t/sI8ILQSIFnZcq5d0oWjGVSXH7Wrn3qaczgRvxh4FN1ZJCeqNWjg0O9/XrukA5Rdrcu84Rm6llSASXOYFB8jpfst777Y2hLW+WoB763B3MwsUkUmualZ2qt4xTvHZGmxJTl9ecVSvjayvtnhvbaXSe0jurRtOd/3zGDbKbbHW8jboYid5ftBt0cCbNusJCEqtj+yedKyPlDiTa6/mKessvWotGQ7GMlFR7fWRukX2lA1jyN1qgt6erzF8pN71eSjU+mkZ7ulkC617OsxSlCmqZ7kmSdmlLTo9U0V06bvJSleGKwEpSj3OXYEAqRFRQtxWOingVwaVtrQJX/r5dSh7ciMKayD9cnMgoeCpCN1krZRWob+EoEPjC4R8GIhm5BI36pYy0IK5Gqll3RO2QVDhnJMZcdX4Uy8+bx0ppRg0tCQpHFhfC+gq6EtUvqK3Zg2hZUWaALShi28KloidxPDySvGeCs46Qhuo21yKK476OqotVpaVwUmuPfxwQrBDMb5eMS1iuUmhHh25M2slHIfj/LLYbc+G2DlwFJeKsldZ8bTRrJ7PB91Kycbh4vmyznlS1F4PiD0Uth41pQRUXpcrsjeW6z1tstcxUZ+RCTmLatYP2TZq0bqLaXtiYpc5M1bv35YGvZzp12t88NxiIDkWFkXZFZXDPqfwHI/+7aZAcUoWko+RgMo7NGwREvUKOUgHs35xNPOqkoc4aWozG89bwMse1643TMi7Tp9ut9RdF3J7oqR2zkDTkF/U8nJMFiXwaqPQ9FO00p5rWNX9wlGXF3sAXH5S5kFurIPfV00jOjQq4Bp2TO9yaxUum62h31JLzlWWQWYniVkxB50r9Zbq2cwJxQg/kMfgHZ8JFo4ihS1tu7iXxi57+3B7PboAGmPDFQ0NZzeNqrKAXNPg/soCL2q0EvfTgRbNUAkKUJsRTSJtLjuPtd9ODedq7ItAccW6CwlVE2QjtbgtnB+nh3Tu8cuF1G+IgvqWkopVWS7SS0Ekoj9cMkk+xVegw07M42ivPm8cgISix9BlKKI61ufjU1pUaHpUoy4hCh843XKsHCf0z8UomIGrsmLPPNJHzlKxENgtyOK7pZg+Ur8wUlgPjwXSLATiZpeAygklj7FNzjexs3KHo9vOvEJloABt1Z9zs60tzUpYV8+CI0lYx1mOfSqdozOPNJtsYdYJPvcuYi+Kjp2Av90sbB088yQI9IhcgiT0AR7rrWyfhOUg96UcVRFflEh0zIpn9Zouys2L1GM43nGTQNeLXmJyT+IZccMhc4Tpgq1Sck5PU2PpeYSt1MVqLjp5stn6RtnmYx3K18s7vhh+gyUVPuj02oaLfT8cDt++f9s/Ufv6wun9bfO/vT9e+7fG6/t/e3+J9Fuzgml96mEkBSZFWBRTsRezcUR5JE2REU1EGEVjIYkRROxFKBihaQKhUIYIQIfjkxgJHvEQIwKCCr/9+/t7p3oCu1YB2PZfvu1fZv3+/tjvd1283u+/lSHYMairKeqGzxc//pf39edG78nvh9//q/P+XP0e+vG/3ka+/StYHmTgEuhvyH6nYkx+XvvH1zd7n5929Ws/ROW/vb+PXoafH4INXvL1l1HAdP/5t13AErD17/8bb+ZPvAE2AAA= -->
