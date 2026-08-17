"""KnowledgeCompanion — grounded, cited answers from the program knowledge store.

The retrieval half of the transformation knowledge companion: given a natural-language
question, scores every indexed chunk (documents from the SharePoint program library +
SAP system extracts), and returns the top passages with full source citations. The
orchestrating LLM composes the final answer ONLY from these passages.

Auto-ingests on first use if the knowledge store is empty, so a fresh deployment answers
its first question with zero setup.

Stdlib-only on purpose: hot-deployable into a running function app's agents/ file share.
"""
import json
import logging
import math
import re

from agents.basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager

KNOWLEDGE_DIR = "knowledge"
CHUNKS_FILE = "chunks.json"
TOP_K = 6
MAX_CHARS = 7000

# Tokenized-corpus cache so tenant-scale indexes (thousands of passages) are not
# re-tokenized on every question. Keyed by the index's ingested_at stamp.
_token_cache = {"key": None, "tokenized": None}

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "s", "should", "that", "the", "their",
    "them", "there", "this", "to", "was", "we", "what", "when", "where", "which", "who",
    "whom", "whose", "why", "will", "with", "you", "your",
}


def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9/&-]+", text.lower()) if t not in _STOPWORDS and len(t) > 1]


def _tokenize_corpus(chunks, cache_key):
    if _token_cache["key"] == cache_key and _token_cache["tokenized"] is not None:
        return _token_cache["tokenized"]
    tokenized, df = [], {}
    for c in chunks:
        body_terms = _tokens(c["text"])
        head_terms = _tokens(f"{c['title']} {c['section']} {c['workstream']}")
        tokenized.append((body_terms, head_terms))
        for t in set(body_terms) | set(head_terms):
            df[t] = df.get(t, 0) + 1
    _token_cache["key"] = cache_key
    _token_cache["tokenized"] = (tokenized, df)
    return _token_cache["tokenized"]


def _score_chunks(question, chunks, cache_key=None):
    """BM25-flavored keyword scoring with title/section boosts. Deterministic, stdlib-only."""
    q_terms = set(_tokens(question))
    if not q_terms:
        return []

    n = len(chunks)
    tokenized, df = _tokenize_corpus(chunks, cache_key)

    scored = []
    for c, (body_terms, head_terms) in zip(chunks, tokenized):
        score = 0.0
        body_len = max(len(body_terms), 1)
        for t in q_terms:
            tf = body_terms.count(t)
            head_hits = head_terms.count(t)
            if tf == 0 and head_hits == 0:
                continue
            idf = math.log(1 + n / (1 + df.get(t, 0)))
            score += idf * (tf / (tf + 1.2 * (0.25 + 0.75 * body_len / 220.0)))
            score += idf * head_hits * 1.5  # title/section/workstream boost
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1]["doc"], x[1]["section"]))
    return scored


class KnowledgeCompanionAgent(BasicAgent):
    def __init__(self):
        self.name = "KnowledgeCompanion"
        self.metadata = {
            "name": self.name,
            "description": (
                "ALWAYS use this for any question about the S/4HANA transformation program: "
                "workstreams, owners and backups, processes (P2P, O2C, R2R), escalation paths, "
                "governance, timelines, waves, cutover, training, resources, or SAP system data "
                "(company codes, plants, business partners). Returns grounded source passages "
                "with citations. Compose your answer ONLY from the returned passages and always "
                "cite the source documents by title. If the passages do not contain the answer, "
                "say the knowledge base does not cover it — never invent program facts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The user's question, as asked, in natural language",
                    },
                },
                "required": ["question"],
            },
        }
        super().__init__(self.name, self.metadata)

    def _load_index(self):
        storage = get_storage_manager()
        raw = storage.read_file(KNOWLEDGE_DIR, CHUNKS_FILE)
        if raw:
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                logging.warning("KnowledgeCompanion: corrupt index, re-ingesting")
        # First use (or corrupt index): auto-ingest from the default live sources.
        from agents.knowledge_ingest_agent import run_ingest
        return run_ingest()

    def perform(self, **kwargs):
        question = str(kwargs.get("question", "")).strip()
        if not question:
            return json.dumps({"error": "No question provided"})

        try:
            index = self._load_index()
        except Exception as e:
            return json.dumps({"error": f"Knowledge store unavailable: {e}"})

        chunks = index.get("chunks", [])
        if not chunks:
            return json.dumps({"error": "Knowledge store is empty and auto-ingest returned no documents."})

        import time as _time
        t0 = _time.time()
        scored = _score_chunks(question, chunks, cache_key=index.get("ingested_at"))
        searched_ms = int((_time.time() - t0) * 1000)
        doc_count = len({c["doc"] for c in chunks})
        if not scored:
            return json.dumps({
                "question": question,
                "passages": [],
                "instruction": "No relevant passages found. Tell the user the program knowledge base does not cover this and suggest contacting the PMO.",
            })

        passages, used = [], 0
        for rank, (score, c) in enumerate(scored[:TOP_K], start=1):
            text = c["text"]
            if used + len(text) > MAX_CHARS:
                text = text[: max(MAX_CHARS - used, 0)]
            if not text:
                break
            used += len(text)
            passages.append({
                "rank": rank,
                "source": c["title"],
                "section": c["section"],
                "document": c["doc"],
                "author": c["author"],
                "workstream": c["workstream"],
                "url": c["url"],
                "text": text,
            })

        return json.dumps({
            "question": question,
            "knowledge_base_as_of": index.get("ingested_at"),
            "search_stats": {
                "documents_searched": doc_count,
                "passages_searched": len(chunks),
                "passages_retrieved": len(passages),
                "search_ms": searched_ms,
            },
            "passages": passages,
            "instruction": (
                "FIRST line of your answer, verbatim from search_stats: "
                f"'Searched {doc_count:,} program documents ({len(chunks):,} passages) in "
                f"{searched_ms} ms; grounding on the top {len(passages)}.' "
                "Then answer using ONLY these passages. Cite every fact's source as a markdown "
                "link: [document title](url) using each passage's url. Compose across passages "
                "when the answer spans sources (e.g. owner + escalation backup). Keep the answer "
                "under ~120 words unless asked for detail."
            ),
        }, ensure_ascii=False)
