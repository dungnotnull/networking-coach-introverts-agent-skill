# Networking Coach for Introverts

`networking-coach-introverts` is a harness skill in the **Career, Learning & Skills** cluster (idea #198). It builds authentic, low-drain networking strategies for introverts - conversation scripts, event tactics, and a relationship-maintenance system - grounded in social-psychology research on weak ties, social capital, introversion, communication, and reciprocity.

> Recommendations are evidence-based decision-support; validate against your specific context before acting.

## What it does
Given a networking goal (a conference, cold outreach, reconnecting, small talk, a career pivot), the skill runs a research-first, framework-grounded harness that ends in:
- A **multi-dimensional score** (0-100) with disclosed weights and per-dimension citations.
- A **confidence** figure reflecting evidence quality and whether live search was available.
- An **energy-aware strategy** with a weekly session-hour budget and recovery plan.
- **Conversation scripts** (opener / transition / exit) per active channel, passed through authenticity filters.
- A **relationship-maintenance / CRM cadence** (tie tiers A/B/C, give-first rotation, re-engagement protocol).
- A **prioritized roadmap** ranked by impact / effort with confidence-building milestones.
- A **devil's-advocate review** that challenges the skill's own scores before output.

## Harness architecture
```
User input
   |
[1 Intake]            sub-profile-intake
   |
[2 Evidence sync]     SECOND-KNOWLEDGE-BRAIN.md + WebSearch/WebFetch
   |
[3 Gate]              requirement validation (halt on red flags)
   |
[4 Strategy+Scripts]  sub-strategy-designer, sub-script-builder -> scored
   |
[5 Challenge]         devil's-advocate review
   |
[6 Synthesis]         sub-followup-system + sub-networking-roadmap
```

No output path bypasses the validation gate or the quality gates.

## Evaluation frameworks (world-renowned, citable)
- Granovetter - Strength of Weak Ties (`#fw-granovetter-1973`)
- Social capital theory - bonding vs bridging (`#fw-putnam-2000`)
- Introversion research - Cain / temperament science (`#fw-cain-2012`)
- Communication accommodation & active listening (`#fw-giles-1991`)
- Give-and-take reciprocity - Grant Givers (`#fw-grant-2013`)

## Repository layout
```
skills/                        # the skill (markdown harness + sub-skills)
  main.md                      # harness: workflow, gates, scoring, output format
  sub-profile-intake.md        # Stage 1 intake schema + question bank
  sub-strategy-designer.md     # energy-aware strategy + channel/cadence model
  sub-script-builder.md        # script library + authenticity filters + scoring
  sub-followup-system.md       # CRM tiers, cadence, re-engagement protocol
  sub-networking-roadmap.md    # effort x impact roadmap + milestones
  SHARED-INTERFACES.md         # Phase 5: cluster reuse contracts
tools/
  scoring_engine.py            # deterministic rubric, weights, composite, gates
  harness.py                   # pipeline orchestrator + CLI (--demo)
  knowledge_updater.py         # arXiv/domain crawl -> SECOND-KNOWLEDGE-BRAIN.md
tests/
  test-scenarios.md            # 14 scenarios (5 core + 2 edge + 7 adversarial)
  test_harness.py              # 36 unittest cases (stdlib, no deps)
SECOND-KNOWLEDGE-BRAIN.md      # living domain knowledge base
PROJECT-detail.md              # full technical spec
PROJECT-DEVELOPMENT-PHASE-TRACKING.md
CLAUDE.md
```

## Requirements
- Python 3.9+ (standard library only for the engine, harness, and tests).
- Optional: `crawl4ai` for domain-source crawling in `knowledge_updater.py` (the arXiv path uses only the standard library; crawl4ai degrades gracefully if absent).
- The skill itself runs as a markdown harness in a Claude-style environment with `WebSearch`/`WebFetch`/`Read`/`Write`/`Bash` tools (graceful offline mode when web tools are unavailable).

## Quickstart

### Smoke-test the harness wiring
```
python tools/harness.py --demo
```
Runs a fully-specified end-to-end example and prints the scored report headline + roadmap. No model, network, or API calls.

### Run the test suite
```
python tests/test_harness.py
```
36 standard-library `unittest` cases covering the gate, scoring math, roadmap prioritization, devil's-advocate enforcement, authenticity filters, tier cap, and degraded-mode behavior.

### Grow the knowledge brain (weekly cron)
```
python tools/knowledge_updater.py            # live fetch + append
python tools/knowledge_updater.py --dry-run  # fetch + print, no write
python tools/knowledge_updater.py --sources arxiv --limit 25
```
Fetches recent arXiv papers (cs.SI, cs.CY) over HTTPS, scores by recency/keyword relevance, dedupes by URL hash, and appends date-stamped entries to `SECOND-KNOWLEDGE-BRAIN.md`. Network errors degrade gracefully (exit 0).

### Run a real pipeline from a JSON input file
```
python tools/harness.py --input path/to/inputs.json
```
`inputs.json` contains `intake_raw`, `scripts`, `question_bank`, `dimension_scores`, `followup`, `roadmap_items`, `milestones`, `ng_components`, and optional `devils_advocate`. Exits 0 on success, 2 on a validation-gate failure, 3 on a quality-gate failure.

## Scoring rubric (fixed, disclosed)
| Dimension | Weight |
|-----------|--------|
| Goal clarity | 0.15 |
| Energy sustainability | 0.20 |
| Authenticity fit | 0.20 |
| Conversation readiness | 0.15 |
| Follow-up consistency | 0.15 |
| Network growth | 0.15 |

Composite = weighted sum of 0-100 dimension scores. Confidence (0-1) reflects evidence tiers and a degraded-mode penalty. See `SECOND-KNOWLEDGE-BRAIN.md` and `tools/scoring_engine.py`.

## Contributing
- Keep the framework set and scoring weights fixed unless you bump the rubric version in `skills/SHARED-INTERFACES.md`.
- Every scored claim must trace to a `#fw-*` anchor in the brain or to an explicit `[assumption: ...]`.
- Add scenarios to `tests/test-scenarios.md` and deterministic assertions to `tests/test_harness.py` for any new gate behavior.
- Run `python tests/test_harness.py` and `python tools/harness.py --demo` before submitting.

## License
MIT - see [LICENSE](LICENSE).