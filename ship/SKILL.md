---
name: "ship"
description: "Commit, push, publish to GitHub Pages, and hand back a VERIFIED live URL. Use whenever the user says \"push it\", \"publish this\", \"ship it\", \"make this live\", \"show me the link so I can test\", or finishes building anything static (single-file HTML app, demo, deck, agent page) that belongs on the web. Invoking this skill IS the authorization to commit and push — do not ask for permission again."
---

# Ship: commit → push → publish → verified live URL

The deliverable of this skill is ONE thing: a live URL that has been **verified to serve the newest content**. Not "pushed", not "Pages enabled" — a link Kody can click right now and see the new thing.

## Step 0 — Guardrail (before anything touches a remote)

Kody runs two RAPP worlds: **my-RAPP** (personal, `kody-w/*` on GitHub) and **work-RAPP** (the work org). Flow is upstream→downstream ONLY: personal→work is fine, **work content must never land in a `kody-w` personal repo**. If the content being shipped originated from work (customer names, work-org repos, internal data, internal transcripts), stop and confirm the destination before pushing. Everything else: proceed without asking.

## Step 1 — Commit

- If not in a git repo: `git init`, then continue.
- Stage the relevant files (not blanket `git add -A` if the directory has obvious junk — check `git status` first).
- Commit message: one line, what changed and why it's visible ("Add particle-sim demo page", not "updates").
- Include the standard co-author trailer.

## Step 2 — Push (create the remote if missing)

- If a remote exists: push to the current branch.
- If no remote: `gh repo create kody-w/<sensible-kebab-name> --public --source . --push`. Derive the name from the project/file, don't ask.
- If push is rejected (remote ahead): pull --rebase and retry once; if there are real conflicts, stop and report — don't force-push.

## Step 3 — Publish to GitHub Pages (for anything static)

Static = single-file HTML apps, demos, decks, docs, anything a browser can render without a server. Kody's default artifact shape is the self-contained single HTML file.

- Check if Pages is already enabled: `gh api repos/kody-w/<repo>/pages` (404 = not enabled).
- Enable if needed: `gh api repos/kody-w/<repo>/pages -X POST -f "source[branch]=main" -f "source[path]=/"` (adjust branch/path to where the HTML lives; if the file isn't `index.html` at the published root, the URL must include the filename).
- The live URL is `https://kody-w.github.io/<repo>/[<file>.html]`.

If the thing is a RAPP agent rather than a page, the publish target is the RAR registry (`kody-w/RAR`, single-file agent publish flow) — push the agent file there instead of enabling Pages.

## Step 4 — Verify it's ACTUALLY live (the step that makes this skill worth having)

GitHub Pages deploys lag and cache. HTTP 200 is not proof — the old version also returns 200.

1. Pick a **marker string** that exists only in the new content (a new heading, a version string, a phrase from this change).
2. Poll: `curl -sL <url> | grep -c "<marker>"` every ~20s, up to ~4 minutes. You can watch the deploy directly with `gh api repos/kody-w/<repo>/pages/builds/latest` (status `built` = done).
3. Only when the marker appears, report success.
4. If 4 minutes pass without the marker: report the URL anyway but say explicitly "pushed, but the live URL is still serving the old version — Pages build status is X". Never present an unverified link as done.

## Step 5 — Report

Final message: the live URL on its own line (clickable), one sentence on what was shipped, and the repo URL. Nothing else unless something went wrong.

## Don'ts

- Don't ask "should I commit/push?" — the invocation is the approval.
- Don't stop after `git push` and call it shipped; the live URL check is the finish line.
- Don't create a new repo when the file already lives in one that has Pages — ship in place.
- Don't publish work/customer content to personal repos (Step 0).

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "marker": {
      "description": "Derived from `<marker>` used in the documented command at line 37.",
      "type": "string"
    },
    "repo": {
      "description": "Derived from `<repo>` used in the documented command at line 26.",
      "type": "string"
    },
    "sensible_kebab_name": {
      "description": "Derived from `<sensible-kebab-name>` used in the documented command at line 19.",
      "type": "string"
    },
    "url": {
      "description": "Derived from `<url>` used in the documented command at line 37.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
git init
git add -A
git status
gh repo create kody-w/<sensible-kebab-name> --public --source . --push
gh api repos/kody-w/<repo>/pages
gh api repos/kody-w/<repo>/pages -X POST -f "source[branch]=main" -f "source[path]=/"
curl -sL <url> | grep -c "<marker>"
gh api repos/kody-w/<repo>/pages/builds/latest
git push
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1:H4sIAAAAAAAC/616a7ejyHLlX9E6/uDupqoEiGfZ17MkQIBAQgIhIbnvcvF+v994rn/7JOicqmqvtn3XzNSHU0JJZkZG7NixA/Tvb2bbBHn19jVrk+TTm+NWYWc2YZ69ff3Xf3+Lw8x5+/pmZn7ivn16S8LMffuK0J/eCrMyUzBSu1kdWon7b7Frmda/ZWY639fksQsWePvnj+HPy/Dnefhf3v726b9YGCV+LFy5Rf7zSvP1fzN1Q/6Y2lbJzzPB5d85MTWr2K1+nvv6Bkz/6+ya2q7C4uWbNyZP07D5tCraOpj/WklYB6smX/FhI7TW6mz6bv1pZWbOKpj/WKYdr8zVjVPFvcixqyTs3JWuyl9Weu2u+sDN3M6tVk3grtoafKjNsV79/jYvvwqb398+LRfvuwRh/fqmDsLi+3Bqxu4ytiz+cUPer1J3WRccOF7V+Upc2Wa2atx6mZdXKy/MwLJuvbLaMHHCzAdmj2Ah8KFuABjs1S91OHvtsxcm7kq4HuWVWRSfVo6b5vNfOwYn9d2sWRXgv1/Bbmazstwkz/x6lWfL7r1rfVmJWZfH87qLmXUcJslK1JbxFw7DaQHf7Eh78fDiwcULv7cojGArJ19lOfi6jlcesL1wqzSs63mO6Zth9gWEzx3MtEjcGkAYxC3IU3c26wPiIRh7+/rvbwkAAghkAU4KIvrprW7col5Qb6czTnywOXBM8wP3yIyiH4Om46w+b38Mo38cnl3X1n8+HKxmPK/syjUbdxXnzvi5X/9ptqw+f17CboMPdd5Wtrv6snxXBz8l5B+WNotwWb5efyy8JM96dkL9U7L9/ZNWn43VWdGuq8/ejKnFjH+1KjOzg7/+JQVe//3tD0OF2YCB9e9vP3Yjf+xmg4xcfa7l1ZKaq/+98sFWq882mP+RcD/N3JB/v53rBcD1OjFndP/5EiAyf3AeRv3tr38DqMjqpmrtGXwABG//sNJAan39ACHAHkKj33H4+vxKxvdLkLyhF7rO98T+Pfs9uwJcO+78TWWCuK5y72fggw/KiVstifYVcMPHzFf6BCbIR9fNVr/99n1tkBWAG7pXOmduDw4JLMwakHm//fZldQJ58aIM15lTO1uuFyZaudlsAfj6I4/MFx9IwIsLH9gAY/GqCv2gARP7Je9q9/tWLzO/zKf6B+AckCsr+GMpvjUrpzLDZPWL5YKkdH/wR5O39swsJghamjfur/MCy55Vm9Wrps9X6vZ8XvV5BQL3FRw2HT/P3/z22+oXkNt1npnJp9W392D/9m2mkxfF/rqY+NtvYGr8fcrCNOALQGv+r19W+wScBPi5LUB0XTN9BcvJ++x1DQIgP76uPjZ6DS/zwSRAi+6n9w0+3LxKW+DzF1cn8/4h4J0P8759X2iB6BwS0Vsc+DHbchdSBdAqQDgB3flhBrDqrLwqT1+G/2KDHQBlVas5/0EJWc4HjvOC/SewY+NW8x6O2Zg/XTYgH18Vqv71E2CfvFgcBLb2wipdzAAlrJk3nNnyPVIzWubArjhwpPeguUntAqdUue0C0/oQEGS7MO5/RgDygYBXNZyHPs9HnoG3OGbOttnsr6tvH3T67dNsSra4JMxa98s8R2sASBcTKzdxOxO4ai419eqXeSkLeDp2m9caL9b9tgpfnnXCyrWbvBqXhMmtLszbehW1ANrvtgH8AWB/+0HJ38DaVd38uuz8shyUyLoGJnwF8FoKJQh8P2ehDYq3D5wwe7IPRlBr/7FedeFC06tffn/bAmuAfAA1EtB2HaZLSVyq4I8EbAtn5qPf3147ipmdtM7rtMCgzAHJA7zx+VUA5zCCk1d/8DP6cZbzTEC/vJeNl7vmrJqdsVTBzP/1exA+Um7lDmHdgNxa2AtQyALItqoWQC4k/uV73N7nzPH6/1Kjvn1ZsbOkfOcRcPcL6vMVAFgEYreeIw1URJ794wKyD2Ne0qcGVsx3gRj88n4eM3BN59f5PIBEP3+ugCG1u0SochsAhDyz3X96x8fMRdXsJpAgcyYAI5v6p+yYj1g1P7TFbAPIC9tdrP9DEDY/gvCnYm/1y6xH/pNyWsKhvUTUX1Z/pqLql4yqXzpq/i+3F+H4vo4JYpT3syScWRoEDUj0Hzn5qgfVl4XHATQd1zPbBAwASHqmDSAfmIU7u3GBm5t4n+fEAyUbOPRlzsuS2aYvL+wwS8IA/72OBeaaCXAg4Oz3IvJCx39bib+tfsFgDBx5ToH3aS/4c8vFvHwG2OXvWuz/Wn4AK0wnmhn7dfd6Hpnj1i/ImF2yHH6uvPUHZBZXgFPPUPgGWgZ3+BI0afJtBehgge0r/MB/VZ43C5stVXupDOFPyT2vMyP+de7rosDfKzzw6begaYr66/r9wF8APwWt9SXMP47+r/88L/Avy+Z//bbE5r2avIAxx+VVPF/SuzJnvM/iYWbe2XGffrZ31ZiVD0j0HQrqVgUO9wEzgIz55aO+gm8BP/8M03dZ/76GB+rprx958OKT4OOe5fZXys1iCgBm1jtL7GdzFzD9IaGwj4Vus75559Ytc9W3svx4+eqXF0mCmxdNNHc49c8SCtRGENDA7D6Y7w8J6bhFkoM2KjH9Vyk0QS34AkJ+Pa9QGJ5dMcMT8BAw9N2WecM8cWY992oqknomxaatgFwBk5YTIF9W53Dp54BeWRQrMLICNgAJshj6olzARMk4F8IPDfUhA34xl8uZx8AkkOzft3stM39TBNVMa+9sCUx9laIZTCjYPk8SkDl/l5T+tprlyrj6DxQGxNIWcwL8BwYKRtaCsvRl9cjbhVt6s7GDd50wO+69toIjzHTzP6fpH9U3yL1XuV19m78H13+Z+XU5wObLSpldM7e9y4bvTgR06JoVMPKdluvWtkFhBjOwRUp9NxrAu66/s+CPFb5+zPxISkCjvTmCxraZO2oQlwJUgHA+04dQ/rQMNv8pO4FOAvCayfXVrf4RFB+FYEHZcup3aTFPNX5/A1J8UYhF5dZzvIFz2+ynDgGIEyBWZm/8ISHwj4XV5RDz0D6cpd13dfIHM4Eh4QyyPlsUC9AFs4Sf2RXov1nHzHu7oBjOdy5qpge7vovP16OJl4QAVX55EgH6h+/6DxgM9Be4HUjR17f9fJK+yn9oQHYul/WraLAf5fv10KEFLhHfu6f17Oj/9aPzmDcNsy63X0L0nZBA7Ku8M5MvP1Z7VWkP6NuXfFsExXsmz/1T83GYf/qjY16K733d18ONxUM/Lf2ual55uHjgOxZftPde8ZbKMKfw7M/vfdkr8O/HeT2DyVZFYto/b/HBmbN+X38X9R8UAHLwD80CkA+vpurXL0tragOd9f2RxfJY7evb3JK+vT+ucoFX6vkxBvAaWKgJ3eXq/REW+PTHx1UvEfbeZ3z74IZv87Mm54OhgPBo0xkyzhK42c/gvAu0NuRsVTMWsxkvjnoDTfPykO5/2mthiL97J5T4053+7Dnj/7Txn0nVv9sOhP5TO+Zni//TvjMV/795dnFt2QL6dV7PsN7Hc2uWwrMdAGwNkJspMGa+mnkG6EBntm2pjPMHi8DAHAGrxe3rH7Mmbw/UkCtUuNE4YvtjfkJkguL8cLfTFbLdcyEj9uF2y3vW887x4YF7MJqK4lrsxcfcgOJ2ZGGmdCxAzFGj0MwuULqufrgogtCCPMJ1pQtTxBqNZDEOAaQon9c3JWGLYHtc87lLkcTVrsdAtNa3B30g+eF0VNNrVJ1v3KDLzBkPwnQXNVmeEEUul0/fRZ7mdefVu7Nib447FPSpEqmKrIT20VEQoyGRrV4WOTmQkqvMeudRmNLDGVq3ieUZZ28wTA33s5FUFKQiA35tYui6832ZZb1SQYhruwu1h98cOfhQn1SRyG5BdEiULW+edvvjNNCK02+ljTZtuT2cloVI8GfN6bEh7or2+ESFkcSjbRJWeNC2vEDIXnoptTtnqo+dAEE9j0thmfL7/nn389uuM5qglNYPsQ7YPZ02G32wh7XSB7dxfSNlnU2VTE8YRtckRKlPyK6t67VieOu+u17GXsRuWfgIH5gQpAM5Xg73cvcIA4U6Vzc358fGo56xdpysnlK9dXtck6NVhqN5IHb5SBahkhu0ntOG6Yct4bt4pD5u/mWtTNVmG1DMcMehx2nskgcCq7WE75i+D/sKodYyd/T1I0GV+s7fH3aIzTSieEu8jsTDM6de93R2ydVH3pS2qTx9NVc2SDEVdQHQLjVXuc1ME+8Z81G7o44EV4RNpEikaL6jXfECXcKTJtYc3jyfj6JWsSrKbbrszXhah/jEpw/z4m+Z4Mlqt3OkEc3NGp7Z5SEl6iM4REwQqmpAup3IY16WMJtqpLUOZdmb2Mfs0KVCJ4cDLnlMRxJRelVpqjQ2JBTc721Ay2YUbbcU49Kufks3+WWbXtAQF+FTcPGkUhFUh7UvMoHDQ4eiW8NFtC6wYaahXKSFir02HSm/g+HKvQfZDmcHW5novi84/qHn60s7TU0SNfdKT7dere63xEU6JzsulxL0YUP5Rp6GqubOhS/gHOsIvsNfVA3FVHIHT3tzSzva83Zu0LTebdHdYQ9Blxu015+wiZ4K+FHR6HbwU1Wtw/OJqgKJ2Zl5OnAnib6LprFlmr1t+k9sXwWXEx07Ok0ZGy2Us4rVic2dwfIbZnZKuL05vjfQPU2qB09dQx12glRWbw2GmYRwfzBE6S4NTthvzuPuJnJ3absTGj5JrmLNt3F0SfYIyRl4gExpPpXXdMhNNTScm8KZLcHdHwfnGG8Hyq+2O59p96PEj88DSOk+I1QXNqHjWO9NrT8/u61kginsY+fmI+tFul/vVNovyd25Iq8PObm2ku9kCPSoGVUT013zYDqudjvNrNJCd9mnyutDHLpEDd9995m4wTFud3IOM8rFx10+SgAwFBbTkZJ0LtswL04ZqzLmOZA4yDf3xnTSHgKK4+tJ1YtgsHFRb0snFUtmz2fBUzh52+1ml9NtG2mdnZRsgRqaV3eAEvsNLkYSo9CUjty4G325sRRjNHhpJScfq+OJl0/9nqyeWEavwcb+YevKW9U7YQHvYEzE4BdJxfS97EPshlYfbddp04HiMm7rXRzTI2kO5JiQG8gWvoh1J08CFqsBcr2LUWBJgn+3KDrH+IG9DFrAw1tbJKGDn2abfKuqoJ/FDgLUn+GTeUbX+3M4Gl24hsp4eJLq+RztUVHUxuOGggKBNPtjbWrPB5z3Pc14OlEkdEMctoYtMtf7iWuTbS5oGJi+CWgvRIr0vs154qG11o4B+VTew621bw/sQaP4pOWfJOFvcnHY3ZN6w8fU5UrQYqUdCYLYZqwe9Hq194nLjqWh7HI5igBzQOdzns3tNmeIEzF6J04korD9gddlqisxQUEaT3R9BqbMpn5otHDdXWPZe4a+H5aidyd3ZbKGTrygHDAA6VDf78joCjHbPKEu7NX1sNbfS4mjbnshyXPMjGwy9p9bYjdse6kjyO0mhTqnLEgSiWCFQrRDW14gOTxyQ1WUlWDFm81U2nc1e1y6tr00pJG3Op2Piklm5lOlcst7bOA9VHET7egHARHWpO/C69IhyAmiLvCmpQh+tyUK4dj7VqUeK+bU5DRzklQ1I+kmecr7W8hA0cD6zCHW2Os+226dozc9EIvRR9adIIYiiJBk1VOK4bYJbZEGFakzkULWJjv4t+1BivdawWA4VakCXBoJ0TxgWg9vmyG98uiwYUFznF4o6rSmeKN5HnZ6JOOyMPhjzN0s7dalCkoijXIat82uMkoJefTwzo3ovVlSexDkAjtq/nErqtujK0bexSj5TFxnN5O1u8tTM54Rn7M3f+cBxZAqkR4GGRcEEqnt+Ox47xWoFNCa31/zXdqpzLnJjd6N18OzvFOqZnMhoaTnSc0ngkviAQsnMu5FIwLSwGSvgYOwE3a8bx8i78Y1Rm5dDNpm5InqmYLfdnxnwRfofL/2O+zAOhJ5XDtssRP2IV+vyVh4jKz4OJbUo7T7cp1GIPtOXU3jicyS0fa65kyDIu8kZ27uLrbDTCNM4fv1iNeGBwsKvlYV7dAxjne88MlOhUui27TM5cof8cvDk6fJeh4KvgbhQsxuH4ue7Ct6DGksvsFQ6vx8QIoPiceCkVxBjyU5YopLvE2fG51TN5rXNl7hQbmP7PAtE3JCjR4woetvzNUT0UppCPIcs1UUQ36CNsWeuvF+mR/vNspcR9FFtvecfWr8lWY7ZDQTtLvdTbDa0TMD2SIn1nhuOMmU8tPDOgLGn2ITZh75qVQZuLzwLGsAAYZzTFN18uCaNQL7O/4UIfCF1NcPJ9zC9E6xhUzcEVbR61L+iNgALa38lBo5x/WuPgTO+XE8UhGDZcS9v+0B3xhFjsG2st8V0V2iqH7QlQs+DUZH16fz8a6eYFNSMDO+9SSiwkUce6I3odDmAost0jZRHCFZhqPewUmuGn3LPdq3Un6EyKiEngQiPfJQpYXCtCTpIKf8rvFjE/TbVL/WdruDdR5YZ6JN4VTVygSf+XKLk9xWbgQSK3DbAFSz0/LO81k2OG29Etfh/dbHt1U36Adk0B+Bf6M4Q8vOncbVCfRkaZ4iu2DH3LTb0ZngQByT4NrLToW5WiyfmScbZFOSDw/i2N6jMyMcMC1NOIPGTdJwNzTVYbxRGUj9oHMNdYWKzWLxRphpZkH+E9nWswy/FDz1gPzSPV+uroC2Oxq2YTjCXS+Sr/E+aYqMhAiD0glBj6CWFJK1uy6DyoMtyqK37t73WcnbqmNnP6ze9/USxfjH/AqKvB4yvHKyhFXWG94zc5lEdBwubxS2NScqWrfb8owYLbxVvHbPXDBy3e68jetJa1tSEad/SnaN+KUS+GvDWZtn+HBx6bW1vV1qYOFaKu6pMQqWdtFz3sYGWFO2F766cALkoLY0OdupOHc37hRwsiVsoJ7odCepd6mtSWYLvNukIbe3/UGWbic/mBxZMPmAOHZVjpwoaO27nBDp106JB0VYPyrbCZrOmGLrilAjP9EGPaVpRVd65kAZpSIl4uX6zfRwSDTZDd870C7ZB5ORb/WY6qdNJoeWg8v7eALS7lFg5cVVn/dN65nlGCgW6yOC4QZCXHjUwwI4g1uJCo7E1Uvy1FOfSccbbNseVRJVLeGwOwwoWk78MPIOud6K2Lg/G2gUwUe9ydsErR32eXv6urG7NgjZg/Jx6TU/aJAD7Uxy9twIp+6WbFD3ACpwJ132CeSB7kdWVadDZIorZaHaHU1UNyMvJ5BrXJIJI/AUMQEtUGS7vcc2z81+ZE+1E5rPEL0/kFwJ9TOjrftCKGIJF9tgXVHHhtnsYPokNSV1POK4QRVN3rTZlbh0ei2lnUkqa4+NG+g2yaJjKbhOuleLj0fBqCnptt9opZE90uLue8FdLEiv4xo/Inq7JK36DBfBmjxomFtOcm6IjVIlki6ffe7oBDEEiq8TwSgup454AT1T+ExOz5R83mlSKdz2cqyghDX3J8crEtAuYnJggaJRGy5zIDGtEOp1gztCBGUwTsVK28J4PuaUhqu959fHwMAFKqi7NPNi0HL4x7ODwyfOpIs9n7cB17EZZ55HZJOZkhieSXXE3Fbe7WJJiKLwluUFtElzoN2dIdigCdydVeKkHfRTc+skH3RqeOJ0jd7mnbR2hb1ZN/6tisrq5tR9SgqH6QDEm3jaj5iQQYl2FteguMjYY0RsjIUDW4kq9KTkxMHAkSrhsWOS3E/10+Gh6G49oa4wnxtS6aF+KE137/CGzSCKOk3qpr9yDxe+t9hZzx5j1l7TdSX7sMF5N5k5aC122pB2VQ1Kfpko84paJbknSF3aH44PZ4ur1YVQeEKvVfUG8VdNeGL0BulQiESODQ3CUBo9XEPk2SLqou3Q8Z53jO1tZcO9c0BLNlcFMTeGkhkiTvQEa1n5GoYf67q4y+1l0sa7fs3SBwVoTlDgY3Llic2TbeHKylS53rHEZit2Tlp7mipsIYRnqbtsPUzavAqdOTbGwdg/Uc8vzYuR+tJWaK0giECTfjVLFVR0G7ojTMJhpYVZUYyxG61GHdQLdfz0LIe0IlsAEl+HOrTjdhHqNEEo92b1GPEz4hvBZGHtjS+cYmidAEnNzfNuePt1oR1Ct6EmuqavoNtD4sKqCNCnSlcOFoAau+6fTyMcjHZzyu6qSKBbIKtaTRsLPq/JoN4xI10bVhs8d9aoRqciPVqnO5B0E5NNoSDvHnlabMl75mbY1LlMFic3TmMfp7bYZ51FyLlj3bzKFnwIe1peaRPoMUfTdiT3ldzKd91MoHsiqFxxVyzEVgwVplNJmRqANqmADWRo1Lg0S8zJz2vQU2oJD7RkjR/0/Gg7AIo0jFypbiOIY2FbnHV1HPsJU7yNZqjZV4JJJ4RE8c9wsN3A4eHulLR1mjE0fBXuOjxd1nv/LnMnay9fJ+s2kWJzvMaE7+CNjjZ4DaXe04RLth/aRHGLBg/TnOjkOJLwLOil83BHqmDQHq2oR8I5uO83LAtxSXoZp+dVNJXI3cPuGZK3ZHbATkUweU7tcUg9IDAKxIQRoGy6cWA1wWEi4oUj4abEWodIxkif2ZAbkCFOxuEe5wfkomIHglLR01rYswKaOlB74sK4U/pWqE5WZF05j8NS1zpvqM1OqK0qBrrAt2TCs8QdC0/3YEAHmHF1FvQf/C6TMziQ1/WB3ms5oaqHNpXIAqdKt1RT+Hx83uoqS+6uEreRH+Ns1o5nKpV1HPCWHblwSwaGfLSKbleO14zUlMPDta+n7AB5DUwCUK01uD6CFsq5HhBvyJ9pAp/rFLKDseqfxU2jrHo8j9i4ts+CnvUDjYSpF9FlTJ8S5V6eJ9+lj6xxk1Gs6lqtlaPjrThO9cbAyHBnCM9zRnU4Xt+u2NHg1YoZ0EvNKU14jNKdMVppUiI9DNWYa21JGO4DblL89jnEo8HgXLbxQvtKV+leBQqDC5SgBdiRpEbawIEqeIdwl7ByVNFsvRdNB1tb5+jqS7qSZ/BEuMmg35jQDhJvfIpPOlZxNrk8r/twT0eu86jzmMIUr1nzIbp32373CFqoHPow9BuKH1KhijVLGOXsSGlijluGspcJs93Q7UaiYi3C6kLQYHJrNnJbXU8bhYfla23EuB17LGjCNo+BE8s+W0fP/oYbddRLG+NJUfH6VsuheWVoe5ft0VD2D0fcRNYpzgXruupoJtnEVeJLJaY5iZqqylPTBigMqwPhec5GVx/C6ezmBo2c4DFwp8piKBGd+i4kojAE9V2KKbmq96iSNWe02LeoutkzCTmebKSz60q/GNSaA1q5cnZ7jKgCkz5Ydh1B4khajoTE6bWDby7ZOq4W9K0zIdMgTlIU3bJ+/Qiz3c2lESTRMbNiPLxhS/faqYPVifqAahfjCSWK8NCxSomKlLiWWtDoEB46XEydqQ3uCVMwCAQa5sfcRhA04WM3o3eBF5p2ppzIAywgTP7wbffmx/bEkFYxpVQp7a1TdySPtE0e+f0Jn8YDFvAG4d/klKhKFZTAE2OeFNLj27ufCdUVRfLB4MMEacZaEh/qPbHuENt77K7SoXLPn7e7aw9zU5nCKOjw9ijeglip0+nKHavz86kRAzNiSJW6tzwEPe4JOXHj2VYe2iRWVqCdn/ERYowRw6BsAhrrKcH7wtmajiLfLNfctYdmgKGiJjur2Z0qA0PvbsTelcYFrTNURu35sYM5UZZMfU+JeSSZDophR/TY+HVDD4ORpyh9xW+RIKd0vraRfU0NG43u4mvyeI4ZF5I8pCHj0eYahL7GcKg7mHe7KI3oMMwNgxWzdhW0PuGnPUtW2REaMe9UkkR/eYzQpTwivHKWiDTtlS6GkAi/ELmkHTOlaNvoxp7FKD/Ga4YwxiSOcUE4rdHTdB9ksQ6Rjs/Pe06g8IEYq5wyDTGW6JSAh7OY32FnlNKIDdt2j2L6uXmeh/iCpAwAXyaLFQfFDUXQwc1SFKayn8XTks9i4kGYFxQoPuw8Ob5DeiLUJKyfrzfOuxZXE9QMR4eVbN9z5CROEHqoyVzkJrZ3I1GoE6wOqDrpjn7o41SyO1SbNXtgrMY1eqKwtsK+6km4rXuC2jxHsd3AdrI1Bhq/AWHDra9m/mxclx9JOHRc4wqdoAliQQM2wEUWdOcEge0cqpsyLsuDGxXGvcg3gQqx+IENCfVQMxeZSnOTnmqpHskdq8r8jdzcQTddsaVst61WWrRX6JJJ5KQhYOQh0/PmQvEE1BQXVjByN+otxXSqrBm1jIGSWmecXdYcIsGLbjfOvqVEyzLk2FvXB3karjFJbE6tS2ThBpb1bqaYa0I5D0VsnVOQuOVxZ1phP6YYBT9RopZPjA7Ru02B8SV9kKETVzkeMw1+QTvSEKeVVPcDD3qBUrzi6y66GBcxhqK6sJDTreETDcZSI34UtBxz5JZUrmEm1hWb3/RjthlC3DvmG+6aqBycXjCEx5zpJAEl4z7tgxlwJhI9hIB3rn60d6TYbeRHelRO8mmMBpcqIOuaSvndJScriQYa9gkZIxmvpmQkKYSqi3L3yDwmRw3G2w1O72SZK3lTCPTVjl1phPeTF5wyEw2L7NHXIQiM5Fuj1AihJWiO7Jtmlun1Oo+HZ29nTe37ChSJj/YRP0nzuncqtki38VN28gHf3KvGins/A0ygpe35np0HJjJuhYPF7F6XiZE4bPYubt9tEaajzS50MCmaMGyNhG643qqnjttfYtHfzr/X/vhhzvzGLQiL9VqTRFn+kjrzr8ADE8UJMEJQlkkhJOx6NAybGxSnKZTEHIsmYIQyTRSxNy4M2+gGpW2EoDcW6ZjuxnVoB7cIwrKWt3jzK22wVWaDvf71bX6l/HV5Pff1px2bHDQLX533d4jLy936L9jyq5f6L/Tbp/9imp3Pvyhovn7+l9cLv7+CG+0QGI58gd9er2brcP5h5MdL5Dpp/fcTz+ccwQbpvy2vo4fm457G9N9/Nf/+U4fXemDFv/0fEDJYpSoyAAA= -->
