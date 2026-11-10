# Production-candidate v1.0 — tool-backed, evidence-first

## What is operational
- Deterministic local dossier creation with `venture_release.py`; existing output directories are not overwritten.
- SHA-256 manifest, audit-friendly outputs and strict research/benchmark completeness gates.
- Structured innovation methodology engine: benchmark, JTBD, Design Thinking, C-K, TRIZ, SCAMPER, Blue Ocean, Lean Startup and AARRR.
- **Real official research providers:** [OpenAlex API](https://docs.openalex.org/) and [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), implemented in `research_connectors.py` with read-only HTTPS requests, explicit opt-in, response limits and failure checks. These retrieve scholarly metadata, not market validation.
- GitHub Actions regression suite with mocked provider response tests. Check the specific workflow run before calling a commit tested.

## Run on a private machine or verified private workspace
Current QCVT repository is **PUBLIC**; do not commit selected topics, confidential business ideas, research, pricing experiments, personal data or credentials.

```bash
python3 -m unittest discover -s skills/opportunity-radar/tests -v

# Create a new, immutable release directory (input schemas in VENTURE-STUDIO.md).
python3 skills/opportunity-radar/scripts/venture_release.py \\
  --selection /private/work/selection.json \\
  --innovation /private/work/innovation.json \\
  --output-dir /private/work/releases/v1

# Opt-in to an official metadata source; use only when needed.
python3 skills/opportunity-radar/scripts/research_connectors.py \\
  --provider openalex --query "SELECTED RESEARCH QUESTION" --limit 10 \\
  --allow-network --output /private/work/evidence/openalex.json
python3 skills/opportunity-radar/scripts/research_connectors.py \\
  --provider crossref --query "SELECTED RESEARCH QUESTION" --limit 10 \\
  --allow-network --output /private/work/evidence/crossref.json
```

These sources help discover original studies. They are **not sufficient** to establish pain, competition, willingness to pay, market size or commercial differentiation. Record original study URLs and inspect primary text before promoting any claim to observed evidence.

## Tool selection and results hierarchy
1. **Official sources and primary studies:** regulatory and government datasets, official vendor documentation/pricing, OpenAlex/Crossref discovery. Source dates, authors, primary-vs-secondary lineage and contradictions required.
2. **Direct user signals:** interviews, product reviews, support communities and behavior, with selection bias disclosed. No invented interviews.
3. **Existing products:** official pricing, demos, changelogs, integrations and substitute workflows. Compare same criteria across alternatives.
4. **Innovation methods:** C-K/Design Thinking/JTBD/TRIZ/Blue Ocean, each with evidence IDs and falsifiable claims. No automatic claim of originality.
5. **Implementation:** [GitHub Spec Kit](https://github.com/github/spec-kit) for specs and tasks **after customer evidence**; optional [LangGraph](https://github.com/langchain-ai/langgraph) for orchestration; [GPT Researcher](https://github.com/assafelovic/gpt-researcher) for deeper synthesis only after security, accuracy and cost evaluation. None are installed or invoked by this release.
6. **Business results:** customer commitments and actual receipts > measured conversion/retention > source observations > surveys > estimates > ideas.

## Production hardening still required
- Authenticated private workspace, secret management, least-privilege credentials and backup/restore drills.
- Provider retries, rate-limit handling, citations to original full text, semantic deduplication and provenance checks.
- Human-in-the-loop approvals, sandboxed external skill execution and prompt-injection isolation.
- End-to-end source integration tests, security scans and deployment observability.
- Actual commercial experiments, billing integration and measured unit economics.

**Release classification:** offline production-candidate for **dossier generation**, not a deployed autonomous venture platform. No customer acquisition, billing, deployment or money-making claim is implied.
