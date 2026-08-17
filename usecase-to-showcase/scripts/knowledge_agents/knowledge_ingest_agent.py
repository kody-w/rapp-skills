"""KnowledgeIngest — pulls program knowledge sources into the platform's knowledge store.

Fetches a SharePoint-shaped document library and an SAP-shaped OData gateway (by default the
synthetic Project Phoenix sources on the rapp-static-apis commons), chunks every document by
markdown section, and writes a retrieval index into storage directory 'knowledge'.

Stdlib-only on purpose: this file can be hot-deployed into a running function app's agents/
file share with no dependency changes.
"""
import json
import logging
import re
import urllib.request
from datetime import datetime, timezone

from agents.basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager

DEFAULT_SHAREPOINT_LIBRARY = (
    "https://raw.githubusercontent.com/kody-w/rapp-static-apis/main/"
    "sharepoint/api/v1/sites/phoenix/documents.json"
)
DEFAULT_SAP_REGISTRY = (
    "https://raw.githubusercontent.com/kody-w/rapp-static-apis/main/sap/registry.json"
)
KNOWLEDGE_DIR = "knowledge"
CHUNKS_FILE = "chunks.json"
FETCH_TIMEOUT = 15


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "rapp-knowledge-ingest/1.0"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        return resp.read().decode("utf-8")


def _chunk_markdown(doc_meta, text):
    """Split a markdown doc into per-section chunks, keeping the doc title as context."""
    lines = text.split("\n")
    doc_title = doc_meta.get("title") or doc_meta.get("name", "")
    chunks, section, buf = [], "Overview", []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            chunks.append({
                "doc": doc_meta.get("name", ""),
                "title": doc_title,
                "section": section,
                "author": (doc_meta.get("author") or {}).get("displayName", ""),
                "workstream": doc_meta.get("workstream", ""),
                "url": doc_meta.get("webUrl") or doc_meta.get("raw_url", ""),
                "text": body,
            })

    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            flush()
            buf = []
            if m.group(1) == "#":
                section = "Overview"
                buf.append(line)  # keep the doc heading with the first chunk
            else:
                section = m.group(2).strip()
                buf.append(line)
        else:
            buf.append(line)
    flush()
    return chunks


def _ingest_sharepoint(library_url):
    """Walk the listing (following Graph @odata.nextLink pages when present) and
    fetch every document concurrently — tenant-scale corpora ingest in seconds,
    not minutes."""
    from concurrent.futures import ThreadPoolExecutor

    rows, url, pages = [], library_url, 0
    while url and pages < 100:
        listing = json.loads(_fetch(url))
        rows.extend(listing.get("value", []))
        url = listing.get("@odata.nextLink")
        pages += 1

    def fetch_one(doc):
        target = doc.get("@microsoft.graph.downloadUrl") or doc.get("raw_url")
        if not target:
            return []
        try:
            return _chunk_markdown(doc, _fetch(target))
        except Exception as e:
            logging.warning(f"KnowledgeIngest: failed to fetch {target}: {e}")
            return []

    chunks = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        for result in pool.map(fetch_one, rows):
            chunks.extend(result)
    return chunks, len(rows)


def _ingest_sap(registry_url):
    """Turn each SAP entity set into compact system-of-record chunks."""
    registry = json.loads(_fetch(registry_url))
    system = registry.get("gateway_url", "SAP gateway")
    chunks = []
    for entry in registry.get("entries", []):
        try:
            payload = json.loads(_fetch(entry["raw_url"]))
        except Exception as e:
            logging.warning(f"KnowledgeIngest: failed to fetch {entry.get('raw_url')}: {e}")
            continue
        rows = payload.get("d", {}).get("results", [])
        lines = []
        for r in rows:
            fields = {k: v for k, v in r.items() if k != "__metadata" and v not in (None, "")}
            lines.append("; ".join(f"{k}={v}" for k, v in fields.items()))
        if not lines:
            continue
        chunks.append({
            "doc": entry["name"],
            "title": f"SAP {entry.get('service', '')} — {entry.get('entity_set', '')}",
            "section": "System of record extract",
            "author": "SAP gateway",
            "workstream": "SAP system data",
            "url": entry["raw_url"],
            "text": f"Live extract from {system}, entity set {entry.get('entity_set')} "
                    f"({len(rows)} records):\n" + "\n".join(lines),
        })
    return chunks, len(registry.get("entries", []))


def run_ingest(sharepoint_url=None, sap_url=None):
    """Shared with KnowledgeCompanion for first-call auto-ingest."""
    sharepoint_url = sharepoint_url or DEFAULT_SHAREPOINT_LIBRARY
    sap_url = sap_url or DEFAULT_SAP_REGISTRY

    sp_chunks, sp_docs = _ingest_sharepoint(sharepoint_url)
    sap_chunks, sap_sets = _ingest_sap(sap_url)
    all_chunks = sp_chunks + sap_chunks

    index = {
        "ingested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {"sharepoint_library": sharepoint_url, "sap_registry": sap_url},
        "counts": {"sharepoint_documents": sp_docs, "sap_entity_sets": sap_sets,
                   "chunks": len(all_chunks)},
        "chunks": all_chunks,
    }
    storage = get_storage_manager()
    storage.ensure_directory_exists(KNOWLEDGE_DIR)
    storage.write_file(KNOWLEDGE_DIR, CHUNKS_FILE, json.dumps(index, ensure_ascii=False))
    return index


class KnowledgeIngestAgent(BasicAgent):
    def __init__(self):
        self.name = "KnowledgeIngest"
        self.metadata = {
            "name": self.name,
            "description": (
                "Refreshes the program knowledge store by re-ingesting the SharePoint program "
                "document library and the SAP system extracts. Use when asked to refresh, "
                "re-index, or check the status of the knowledge base."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["refresh", "status"],
                        "description": "refresh = re-fetch all sources and rebuild the index; status = report what is currently indexed",
                    },
                    "sharepoint_library_url": {
                        "type": "string",
                        "description": "Optional override for the SharePoint document-library listing URL",
                    },
                    "sap_registry_url": {
                        "type": "string",
                        "description": "Optional override for the SAP gateway registry URL",
                    },
                },
                "required": ["action"],
            },
        }
        super().__init__(self.name, self.metadata)

    def perform(self, **kwargs):
        action = kwargs.get("action", "status")
        if action == "refresh":
            try:
                index = run_ingest(kwargs.get("sharepoint_library_url"),
                                   kwargs.get("sap_registry_url"))
            except Exception as e:
                return json.dumps({"error": f"Ingest failed: {e}"})
            return json.dumps({"status": "success", "ingested_at": index["ingested_at"],
                               "counts": index["counts"]})

        storage = get_storage_manager()
        raw = storage.read_file(KNOWLEDGE_DIR, CHUNKS_FILE)
        if not raw:
            return json.dumps({"status": "empty",
                               "message": "Knowledge store is empty. Run action=refresh to ingest."})
        index = json.loads(raw)
        return json.dumps({"status": "ready", "ingested_at": index.get("ingested_at"),
                           "sources": index.get("sources"), "counts": index.get("counts")})
