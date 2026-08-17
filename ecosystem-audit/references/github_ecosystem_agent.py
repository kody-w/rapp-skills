"""github_ecosystem_agent.py — ecosystem inventory, velocity, traction, drift.

ONE sacred agent.py that answers "what is actually going on in this GitHub
org/user's ecosystem?" without a human running twenty `gh` one-liners. Drop it
into any RAPP brainstem's agents/ directory and it works: just BasicAgent,
stdlib only, no LLM required, no API key required (it will use one if it can
find one).

WHY IT EXISTS
-------------
The 2026-07-28 RAPP audit was done by hand: list repos, count the family,
count what was created inside the window, probe commits per repo, total the
stars, then fetch the "canonical" spec mirrors and diff them. It found a real
defect -- RAPP-Bible claimed ecosystem-spec.json was published byte-identical
to two grail mirrors (rapp-god + rapp-map); rapp-map served a 14-byte
`404: Not Found`, and rapp-god had silently flipped schema to
`rapp-god-ecosystem-candidate/2.0` with `status: quarantined-candidate` and
`agent_execution: disabled-owner-gated`. The doc that is supposed to lose that
argument had not noticed for two days.

That class of bug is invisible to a star count and invisible to CI, because
nothing is broken -- two files merely stopped agreeing. This agent makes the
check cheap enough to run on a schedule.

WHAT IT DOES
------------
Four stages, each independently useful, each degradable:

  inventory  -- every public repo, family match, created-in-window, dormancy
  velocity   -- commits inside the window for the top-N most recently pushed
  traction   -- star distribution, and the "documented core vs actual work"
                mismatch (a repo the docs call Tier 1 sitting at zero)
  drift      -- given URLs ASSERTED to be byte-identical, prove it: sha256
                each, group them, flag 404s/non-JSON, and surface the
                self-describing status fields (schema/version/status) so a
                quarantine flip is loud instead of silent

DISCIPLINE (borrowed from rapp_factory_agent.py)
------------------------------------------------
  * Every stage is an _Internal-prefixed persona, so a brainstem's *Agent
    discovery exposes only GitHubEcosystem (via the GitHubEcosystemAgent
    alias).
  * Bounded work: _MAX_VELOCITY_REPOS caps the per-repo commit probes, which
    are the only stage that costs one API call per repo. Everything else is
    paginated list traffic.
  * Errors RAISE inside a stage. They never flow downstream as prose. A stage
    failure returns {"status": "error", "failed_stage": ..., "completed_stages":
    [...]} rather than letting an HTTP 403 become a finding.
  * The drift stage reports what it MEASURED, never what it inferred. A mirror
    that 404s is recorded as unreachable, not as "drifted" -- those are
    different failures with different fixes.

Network reads are GET-only. This agent never writes to GitHub.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

try:                                    # brainstem layout
    from agents.basic_agent import BasicAgent
except ImportError:                     # flat bundle (skill zip)
    try:
        from basic_agent import BasicAgent
    except ImportError:                 # last resort — stay self-contained
        class BasicAgent:               # type: ignore[no-redef]
            def __init__(self, name, metadata):
                self.name, self.metadata = name, metadata


# --- bounds ---------------------------------------------------------------
# Commit probes are one API call per repo and are the only stage that scales
# with repo count. 25 covers "what is being worked on" for any real ecosystem;
# past that you are measuring archaeology, not velocity.
_MAX_VELOCITY_REPOS = 25
# GitHub caps commit list responses at 100 per page. We deliberately do not
# paginate: past 100 commits in a window the exact number stops carrying
# information, so we report "100+" and move on.
_COMMIT_PAGE_CAP = 100
_MAX_REPO_PAGES = 10                    # 10 * 100 = 1000 repos
_HTTP_TIMEOUT = 20
_API = "https://api.github.com"


class _StageError(Exception):
    """A stage refused. Carries the stage name so perform() can report it."""

    def __init__(self, stage, detail):
        self.stage, self.detail = stage, detail
        super().__init__(detail)


def _utc_now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# --- transport ------------------------------------------------------------
class _Http:
    """GET-only GitHub/raw client. Finds a token if one exists; works without."""

    def __init__(self, token=None):
        self.token = token or self._discover_token()
        self.calls = 0

    @staticmethod
    def _discover_token():
        for var in ("GITHUB_TOKEN", "GH_TOKEN"):
            val = os.environ.get(var)
            if val:
                return val.strip()
        try:                            # the gh CLI is the common local case
            out = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True, text=True, timeout=10,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
        return None

    def _open(self, url, accept):
        req = urllib.request.Request(url, headers={
            "Accept": accept,
            "User-Agent": "rapp-github-ecosystem-agent",
        })
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        self.calls += 1
        return urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT)

    def api(self, path):
        """GET an api.github.com path. Returns parsed JSON. Raises on HTTP error."""
        url = path if path.startswith("http") else f"{_API}{path}"
        with self._open(url, "application/vnd.github+json") as resp:
            return json.loads(resp.read().decode("utf-8"))

    def api_soft(self, path, default=None):
        """api() that swallows HTTP errors -- for probes where absence is data."""
        try:
            return self.api(path)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
            return default

    def raw(self, url):
        """GET arbitrary content. Returns (bytes, http_status, error_or_None)."""
        try:
            with self._open(url, "*/*") as resp:
                return resp.read(), resp.status, None
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read()
            except OSError:
                body = b""
            return body, exc.code, f"HTTP {exc.code}"
        except (urllib.error.URLError, OSError) as exc:
            return b"", 0, f"{type(exc).__name__}: {exc}"


# --- stages ---------------------------------------------------------------
class _InternalInventory(BasicAgent):
    """Every public repo for an owner, plus family/window/dormancy shape."""

    name = "_InternalInventory"

    def __init__(self, http=None):
        self.http = http
        super().__init__(self.name, {"name": self.name, "description":
                                     "List repos and classify them.",
                                     "parameters": {"type": "object", "properties": {}}})

    def perform(self, owner=None, family=None, since=None, **_):
        if not owner:
            raise _StageError("inventory", "owner is required")
        http = self.http or _Http()
        repos, page = [], 1
        while page <= _MAX_REPO_PAGES:
            try:
                batch = http.api(
                    f"/users/{owner}/repos?per_page=100&page={page}&sort=pushed"
                )
            except urllib.error.HTTPError as exc:
                if page == 1:
                    raise _StageError(
                        "inventory",
                        f"cannot list repos for {owner!r}: HTTP {exc.code}",
                    ) from exc
                break                   # partial list beats no list
            if not isinstance(batch, list) or not batch:
                break
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        if not repos:
            raise _StageError("inventory", f"{owner!r} has no public repos")

        pattern = None
        if family:
            pattern = re.compile(family, re.IGNORECASE)

        rows, fam, created_in_window, dormant = [], [], 0, 0
        for r in repos:
            name = r.get("name") or ""
            desc = r.get("description") or ""
            row = {
                "name": name,
                "description": desc[:120],
                "stars": r.get("stargazers_count", 0),
                "language": (r.get("language") or "-"),
                "pushed_at": (r.get("pushed_at") or "")[:10],
                "created_at": (r.get("created_at") or "")[:10],
                "fork": bool(r.get("fork")),
                "archived": bool(r.get("archived")),
            }
            row["in_family"] = bool(pattern and (pattern.search(name) or pattern.search(desc)))
            if row["in_family"]:
                fam.append(name)
            if since and row["created_at"] and row["created_at"] >= since[:10]:
                created_in_window += 1
            if since and row["pushed_at"] and row["pushed_at"] < since[:10]:
                dormant += 1
            rows.append(row)

        return {
            "owner": owner,
            "total_public_repos": len(rows),
            "family_pattern": family,
            "family_count": len(fam),
            "created_in_window": created_in_window,
            "dormant_in_window": dormant,
            "repos": rows,
        }


class _InternalVelocity(BasicAgent):
    """Commits inside the window for the most recently pushed repos."""

    name = "_InternalVelocity"

    def __init__(self, http=None):
        self.http = http
        super().__init__(self.name, {"name": self.name, "description":
                                     "Count commits per repo in a window.",
                                     "parameters": {"type": "object", "properties": {}}})

    def perform(self, owner=None, repos=None, since=None, limit=None, pinned=None, **_):
        http = self.http or _Http()
        repos = repos or []
        limit = min(int(limit or _MAX_VELOCITY_REPOS), _MAX_VELOCITY_REPOS)
        # Most-recently-pushed first: that is where the work is. Pinned repos
        # (the ones the docs call canonical) jump the queue -- "not probed" is
        # not an acceptable answer about a repo someone declared load-bearing.
        pins = {p.lower() for p in (pinned or [])}
        ordered = sorted(repos, key=lambda r: r.get("pushed_at") or "", reverse=True)
        head = [r for r in ordered if r["name"].lower() in pins]
        tail = [r for r in ordered if r["name"].lower() not in pins]
        ordered = head + tail
        probed, total = [], 0
        for r in ordered[:max(limit, len(head))]:
            commits = http.api_soft(
                f"/repos/{owner}/{r['name']}/commits"
                f"?since={since}&per_page={_COMMIT_PAGE_CAP}",
                default=None,
            )
            if commits is None:         # empty repo, or no access -- not a failure
                probed.append({"repo": r["name"], "commits": None, "note": "unreadable"})
                continue
            n = len(commits) if isinstance(commits, list) else 0
            capped = n >= _COMMIT_PAGE_CAP
            total += n
            probed.append({
                "repo": r["name"],
                "commits": n,
                "capped": capped,
                "display": f"{n}+" if capped else str(n),
                "last_commit": (
                    (commits[0].get("commit", {}).get("author", {}) or {}).get("date")
                    if n else None
                ),
            })
        probed.sort(key=lambda p: (p["commits"] is None, -(p["commits"] or 0)))
        return {
            "window_since": since,
            "repos_probed": len(probed),
            "commits_observed": total,
            "note": f"counts cap at {_COMMIT_PAGE_CAP}; '+' means at least that many",
            "by_repo": probed,
        }


class _InternalTraction(BasicAgent):
    """Star distribution, and documented-core vs actual-attention mismatch."""

    name = "_InternalTraction"

    def __init__(self):
        super().__init__(self.name, {"name": self.name, "description":
                                     "Summarize stars and find neglected cores.",
                                     "parameters": {"type": "object", "properties": {}}})

    def perform(self, repos=None, velocity=None, core_repos=None, **_):
        repos = repos or []
        total = sum(r.get("stars", 0) for r in repos)
        starred = [r for r in repos if r.get("stars", 0) > 0]
        top = sorted(repos, key=lambda r: -r.get("stars", 0))[:10]

        by_name = {v["repo"]: v for v in (velocity or {}).get("by_repo", [])}
        mismatches = []
        for core in (core_repos or []):
            match = next((r for r in repos if r["name"].lower() == core.lower()), None)
            if not match:
                mismatches.append({"repo": core, "finding": "declared core repo not found"})
                continue
            v = by_name.get(match["name"], {})
            probed = "commits" in v and v.get("commits") is not None
            commits = v.get("commits") or 0
            if not probed:
                finding = "declared core, but velocity could not be measured"
            elif match["stars"] < 2 and commits < 10:
                finding = ("declared core, but near-zero attention and low "
                           "velocity -- docs and effort disagree")
            else:
                finding = "declared core, active"
            mismatches.append({
                "repo": match["name"],
                "stars": match["stars"],
                "commits_in_window": v.get("display", "not probed"),
                "finding": finding,
            })

        return {
            "total_stars": total,
            "repos_with_any_star": len(starred),
            "repos_with_zero_stars": len(repos) - len(starred),
            "top_by_stars": [{"repo": r["name"], "stars": r["stars"]} for r in top],
            "declared_core_check": mismatches,
        }


class _InternalDriftAudit(BasicAgent):
    """Prove or disprove a byte-identical claim across asserted mirrors."""

    name = "_InternalDriftAudit"

    def __init__(self, http=None):
        self.http = http
        super().__init__(self.name, {"name": self.name, "description":
                                     "Hash asserted mirrors and report divergence.",
                                     "parameters": {"type": "object", "properties": {}}})

    # Fields a self-describing spec uses to announce what it now is. A silent
    # flip in any of these is the failure mode this stage exists to catch.
    _STATUS_FIELDS = ("schema", "version", "status", "spec_version")

    def perform(self, mirrors=None, **_):
        mirrors = mirrors or []
        if not mirrors:
            return {"checked": 0, "note": "no mirrors asserted; drift audit skipped"}
        http = self.http or _Http()

        observed = []
        for m in mirrors:
            url = m if isinstance(m, str) else (m or {}).get("url")
            label = (m or {}).get("label") if isinstance(m, dict) else None
            if not url:
                raise _StageError("drift", f"mirror entry has no url: {m!r}")
            body, status, err = http.raw(url)
            entry = {
                "label": label or url.split("/")[-1],
                "url": url,
                "http_status": status,
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest() if body else None,
                "reachable": err is None and status == 200,
                "error": err,
            }
            # A 200 that is really a 404 page is the exact trap that hid the
            # rapp-map miss: raw.githubusercontent serves a 14-byte body.
            if body[:14] == b"404: Not Found":
                entry["reachable"] = False
                entry["error"] = "body is a '404: Not Found' sentinel, not content"
            if entry["reachable"]:
                try:
                    doc = json.loads(body.decode("utf-8"))
                    entry["json"] = True
                    if isinstance(doc, dict):
                        entry["declares"] = {
                            k: doc[k] for k in self._STATUS_FIELDS if k in doc
                        }
                except (ValueError, UnicodeDecodeError):
                    entry["json"] = False
            observed.append(entry)

        live = [o for o in observed if o["reachable"]]
        groups = {}
        for o in live:
            groups.setdefault(o["sha256"], []).append(o["label"])
        unreachable = [o["label"] for o in observed if not o["reachable"]]

        if not live:
            verdict = "BROKEN: no asserted mirror is reachable"
        elif unreachable:
            verdict = (
                f"BROKEN: byte-identical claim is unverifiable -- "
                f"{len(unreachable)} of {len(observed)} mirrors unreachable "
                f"({', '.join(unreachable)})"
            )
        elif len(groups) > 1:
            verdict = f"DRIFTED: {len(live)} mirrors resolved to {len(groups)} distinct hashes"
        else:
            verdict = f"ALIGNED: {len(live)} mirrors are byte-identical"

        declared = [o["declares"] for o in live if o.get("declares")]
        return {
            "checked": len(observed),
            "verdict": verdict,
            "aligned": len(groups) == 1 and not unreachable and bool(live),
            "distinct_hashes": len(groups),
            "hash_groups": {h[:16]: names for h, names in groups.items()},
            "unreachable": unreachable,
            "declared_identity": declared,
            "mirrors": observed,
        }


# --- public capability ----------------------------------------------------
class GitHubEcosystem(BasicAgent):
    """Inventory + velocity + traction + drift for a GitHub owner's ecosystem."""

    name = "GitHubEcosystem"

    def __init__(self):
        self.metadata = {
            "name": self.name,
            "description": (
                "Audit a GitHub owner's whole ecosystem: repo inventory and "
                "family match, commit velocity in a window, star traction, and "
                "-- most importantly -- a drift audit that proves or disproves "
                "a 'these mirrors are byte-identical' claim and surfaces silent "
                "spec status flips. Read-only, stdlib, no LLM required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string",
                              "description": "GitHub user or org, e.g. 'kody-w'."},
                    "family": {"type": "string",
                               "description": "Regex matched against repo name and "
                                              "description to count a family, e.g. "
                                              "'rapp|brainstem'."},
                    "days": {"type": "integer",
                             "description": "Window size in days (default 30)."},
                    "velocity_limit": {"type": "integer",
                                       "description": f"Repos to probe for commits "
                                                      f"(max {_MAX_VELOCITY_REPOS})."},
                    "core_repos": {"type": "array", "items": {"type": "string"},
                                   "description": "Repos your docs call canonical. "
                                                  "Checked against real attention."},
                    "mirrors": {"type": "array",
                                "description": "URLs asserted to be byte-identical "
                                               "copies of one document. Each may be a "
                                               "string or {label,url}.",
                                "items": {"type": "string"}},
                },
                "required": ["owner"],
            },
        }
        super().__init__(self.name, self.metadata)

    def perform(self, owner=None, family=None, days=30, velocity_limit=None,
                core_repos=None, mirrors=None, token=None, **_):
        completed = []
        http = _Http(token=token)
        since = _iso(_utc_now() - timedelta(days=int(days or 30)))
        try:
            inv = _InternalInventory(http).perform(
                owner=owner, family=family, since=since)
            completed.append("inventory")

            scope = [r for r in inv["repos"] if r["in_family"]] if family else inv["repos"]
            scope = [r for r in scope if not r["fork"] and not r["archived"]]
            # A declared core repo must be measured even if it falls outside the
            # family regex -- otherwise the core check reports "not probed" and
            # the whole comparison is vacuous.
            pins = {c.lower() for c in (core_repos or [])}
            if pins:
                have = {r["name"].lower() for r in scope}
                scope += [r for r in inv["repos"]
                          if r["name"].lower() in pins and r["name"].lower() not in have]

            vel = _InternalVelocity(http).perform(
                owner=owner, repos=scope, since=since, limit=velocity_limit,
                pinned=core_repos)
            completed.append("velocity")

            trac = _InternalTraction().perform(
                repos=inv["repos"], velocity=vel, core_repos=core_repos)
            completed.append("traction")

            drift = _InternalDriftAudit(http).perform(mirrors=mirrors)
            completed.append("drift")
        except _StageError as exc:
            return {
                "status": "error",
                "failed_stage": exc.stage,
                "detail": exc.detail,
                "completed_stages": completed,
            }

        return {
            "status": "ok",
            "owner": owner,
            "window_days": int(days or 30),
            "window_since": since,
            "authenticated": bool(http.token),
            "api_calls": http.calls,
            "completed_stages": completed,
            "inventory": {k: v for k, v in inv.items() if k != "repos"},
            "velocity": vel,
            "traction": trac,
            "drift": drift,
            "headline": self._headline(inv, vel, trac, drift),
        }

    @staticmethod
    def _headline(inv, vel, trac, drift):
        bits = [
            f"{inv['total_public_repos']} public repos",
        ]
        if inv.get("family_pattern"):
            bits.append(f"{inv['family_count']} in family /{inv['family_pattern']}/")
        bits.append(f"{inv['created_in_window']} created in window")
        bits.append(f"{vel['commits_observed']}+ commits across "
                    f"{vel['repos_probed']} probed repos")
        bits.append(f"{trac['total_stars']} total stars "
                    f"({trac['repos_with_zero_stars']} repos at zero)")
        if drift.get("checked"):
            bits.append(f"drift: {drift['verdict']}")
        return " | ".join(bits)


class GitHubEcosystemAgent(GitHubEcosystem):
    """Discovery alias -- brainstems look for a *Agent class."""
