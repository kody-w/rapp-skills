# Making a deployed Copilot Studio agent actually answer

A factory-generated two-solution suite imports and publishes cleanly and the agent still says the data
is not loaded, or asks the user to upload a file. Nothing is broken. The MCP
servers are in the environment; they are just not attached, and there is no API
for attaching them. This is the manual step.

## The four gates, in order

### 1. Attach the tool, per agent

Build → **Tools** → **Add tool** → **Model Context Protocol (MCP)** → search the
connector name → click the `<Name> MCP Server` row.

### 2. Create the connection

The panel shows **Not connected**. Click it → **Create new connection** →
**Create**. Then **Add**. The attach is not complete without the connection, and
the tool chip will not appear.

### 3. Authentication mode: User → Maker

Click the attached tool chip → **Authentication mode** → **Maker** → **Confirm**.

This is the one that costs an afternoon. It defaults to **User**, and under User
auth the tool attaches, appears in the Tools panel, and publishes with no error -
and never reaches the agent runtime. The agent then truthfully reports it has no
data, which reads like a broken agent rather than a missing setting.

### 4. Verify in Preview, with a citation

Ask a question whose answer can only come from the data, and read the response for
a real record and its citation. "It replied" is not evidence: an agent explaining
that it cannot find anything is behaving correctly and looks like success if you
only glance.

Preview tests the draft, so you can verify before publishing. Do that.

## Repeat per agent

Parent and every connected child. A parent that delegates to a child needs the
attach on both, and the failure surfaces as the *parent* reporting trouble when it
is the child that cannot see data.

## Other things that will bite

- **The attach does not survive a failed publish.** If publish fails, go back to
  Tools and check - the attach will be gone. Re-attach and verify before
  publishing again.
- **Individual tool toggles inside Edit MCP server are greyed out on purpose**
  (`checked: true, disabled: true`). "Enable all tools" forces them. Do not spend
  time trying to flip them.
- **Agent names cap at 30 characters and truncate silently.** Count first.
- **Return does not submit in the chat box.** Click the send arrow.
- **`PvaPublish` returning 200 is not proof.** A bot still provisioning silently
  no-ops. Only `publishedon` flipping counts - poll it, and re-fire publish while
  you wait, since publish is idempotent and the first fire after provisioning
  wins.

## Automating the repetition

The clicks can be driven over CDP once a signed-in browser exists (see
`browser.md`). `scripts/attach_mcp.py` does one connector end to end including the
Maker switch; loop it over the connector names. Discover selectors by reading the
live accessibility tree - Copilot Studio buttons frequently have only an accessible
name, so attribute selectors silently match nothing and report a misleading
"not found".
