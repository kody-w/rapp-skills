# The synthetic enterprise data plane

Enterprise AI demos stall waiting for data access. Invert it: publish the
customer's *systems* as static APIs anyone can curl with no credentials, shaped
exactly like the real thing, so "repoint two URLs at your tenant" is true rather
than hopeful.

Home: `kody-w/rapp-static-apis` (public, MIT). Convention: `rapp-static-api/1.0`,
documented in the repo's `SPEC.md`.

## The rules that keep it trustworthy

- **One hand-authored input** (`seed/`), **one build step** (`build.py`), and a
  generated `registry.json` + `api/v1/status.json`. Nothing else is edited by hand.
- **Idempotent and stable-write**: re-running with no source change produces
  byte-identical output, so scheduled CI never commits noise.
- **Deterministic**: seed every RNG from a stable key (`Random("mount/7|" + key)`
  beats a single sequential seed - it survives refactors), and never read the wall
  clock.
- `sha8` = first 12 hex of sha256 **of the body without its trailing newline** -
  match the house convention or your own audit will report false mismatches.

## Scale is the argument

Fourteen documents proves nothing, and the audience will say exactly that. Generate to
**~300 documents / 1.5-3 MB / thousands of passages**. The cheapest honest way
there: weekly minutes for every workstream across half a year, plus monthly
decision logs, quarterly risk registers, per-role curricula, per-site readiness
reports, and interface specs.

Everything generated must agree with the canon - the same people, the same
decision and risk IDs, the same dates. A generated minute that contradicts the
hand-authored playbook is worse than no minute at all, because the companion will
cite both.

## The four organs, and their real wire shapes

| Mount | Simulates | Shape |
|---|---|---|
| `sharepoint/` | Program document library | Graph `driveItem` pages of 50 with `@odata.nextLink`, plus a Graph Search response sample |
| `sap/` | S/4HANA gateway | OData v2 `{"d": {"__count": "n", "results": [...]}}` with `__metadata` per row |
| `workiq/` | Work-signal insights | Graph-flavoured people, expertise, collaboration, trending |
| `fabriciq/` | Program analytics | Fabric workspace + items, and `executeQueries` result envelopes |

## Get the product names right

Microsoft's intelligence layer is **Work IQ** (signals from M365 work), **Fabric
IQ** (semantic business data), **Foundry IQ** (knowledge retrieval for agents) and
**Web IQ**. There is no "Data IQ" - we shipped a `dataiq/` mount and had to rename
it. Verify a product name before building a mount around it; a wrong name in front
of a Microsoft audience undercuts everything else on the slide.

Both Fabric IQ and Foundry IQ also appear as MCP servers in the Copilot Studio tool
picker, which is worth knowing when the story needs a real product surface.

## Leak gates

Never let these into the commons: real customer or employee names, tenant or
subscription identifiers, or anything from the work estate. Grep before every push.

Two traps found the hard way:

- A `.pyc` embeds the absolute build path, which may contain a real
  name (a home directory, for instance). Set `sys.dont_write_bytecode = True` and delete stale `__pycache__` in the
  build.
- `@microsoft.graph.downloadUrl` is a protocol keyword, not an identifier - a naive
  `@microsoft` grep flags it. Keep protocol fidelity and scope the gate.
