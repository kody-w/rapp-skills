#!/usr/bin/env python3
"""Attach one MCP server to the CURRENT Copilot Studio agent, Maker auth, via CDP.

Usage: attach_mcp.py "<MCP display name>"   e.g. "Governance Escalation MCP"
Assumes the capture Chrome (port 9222) is on the agent's Build page.
Never closes the browser.
"""
import sys, time
from playwright.sync_api import sync_playwright

NAME = sys.argv[1]


def main():
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        pg = next(p for c in b.contexts for p in c.pages if "copilotstudio" in p.url)
        pg.bring_to_front()

        pg.get_by_role("button", name="Add tool").click(); time.sleep(4)
        pg.get_by_test_id("tool-picker-tab-mcp").first.click(); time.sleep(3)
        box = pg.get_by_placeholder("Search").first
        box.click(); box.fill(NAME.replace(" MCP", "")); time.sleep(4)

        pg.get_by_role("button", name=f"{NAME} Server").first.click(); time.sleep(6)

        body = pg.inner_text("body")
        if "Not connected" in body:
            pg.get_by_role("button", name="Not connected").first.click(); time.sleep(4)
            pg.get_by_role("button", name="Create new connection").first.click(); time.sleep(8)
            pg.get_by_role("button", name="Create", exact=True).first.click(); time.sleep(12)

        pg.get_by_role("button", name="Add", exact=True).first.click(); time.sleep(9)

        # auth mode -> Maker
        pg.get_by_text(f"{NAME} Server").first.click(); time.sleep(6)
        try:
            pg.locator('label:has-text("Maker")').first.click(); time.sleep(2)
            pg.get_by_role("button", name="Confirm").first.click(); time.sleep(7)
        except Exception as e:
            print("auth-mode step:", e)

        ok = f"{NAME} Server" in pg.inner_text("body")
        print(f"{NAME}: {'ATTACHED (Maker)' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
