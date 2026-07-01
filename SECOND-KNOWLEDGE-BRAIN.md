# SECOND-KNOWLEDGE-BRAIN.md - Networking Coach for Introverts

> Self-improving domain knowledge base for `networking-coach-introverts` (idea #198, cluster: Career, Learning & Skills). Grown by `tools/knowledge_updater.py`. Maintained under the evidence hierarchy below; every scored claim in a deliverable must trace to an entry here or to an explicit assumption.

## How to use this brain
- The harness loads this file at Stage 2 (Evidence sync). When `WebSearch`/`WebFetch` are available, trend-sensitive figures are refreshed and cited inline; otherwise the skill operates in **degraded (offline-knowledge) mode** and says so explicitly.
- Scoring (Stage 4) cites entries by their anchor ID (e.g. `#fw-granovetter-1973`). An assumption marker `[assumption: ...]` is acceptable only when no citable evidence applies and the assumption is stated in the report.
- The crawl pipeline appends new entries under **Crawled Evidence** with a `<!--hash:...-->` dedup marker; never hand-edit hashes.

## Evidence hierarchy (highest to lowest)
1. Systematic review / meta-analysis
2. Peer-reviewed primary study (RCT, longitudinal, survey with validated scales)
3. Peer-reviewed theoretical / framework paper
4. Expert practitioner literature (HBR, APA, named researchers' outlets)
5. Reputable practitioner blog / trade publication
6. Stated assumption (lowest; must be disclosed)

Scoring confidence is a function of the highest evidence tier reachable per dimension (see `tools/scoring_engine.py::confidence_from_tiers`).

## Core frameworks (scoring backbone)

### Granovetter - Strength of Weak Ties
- **Anchor:** `#fw-granovetter-1973`
- **Citation:** Granovetter, M. S. (1973). The Strength of Weak Ties. *American Journal of Sociology*, 78(6), 1360-1380.
- **Core claim:** Bridging ("weak") ties that connect otherwise separate clusters transmit non-redundant information and disproportionately drive job mobility and opportunity, more than dense bonding ties.
- **Skill application:** Prioritize bridging-tie outreach for opportunity goals (career pivot, job search); do not over-invest in dense bonding networks when growth is the goal.
- **Scoring dimension link:** Network growth.

### Social capital theory - bonding vs bridging
- **Anchor:** `#fw-putnam-2000`
- **Citation:** Putnam, R. D. (2000). *Bowling Alone: The Collapse and Revival of American Community*. Simon & Schuster. See also: Burt, R. S. (1992). *Structural Holes*. Harvard University Press.
- **Core claim:** Bonding capital (close, homogeneous ties) provides emotional support; bridging capital (cross-cutting ties) provides new information and opportunity. Both are needed; their optimal mix depends on the goal.
- **Skill application:** Diagnose the user's current mix; prescribe additions on the deficit side (usually bridging for introverts who already have strong bonding ties).
- **Scoring dimension link:** Network growth, Goal clarity.

### Introversion research - temperament science & energy management
- **Anchor:** `#fw-cain-2012`
- **Citation:** Cain, S. (2012). *Quiet: The Power of Introverts in a World That Can't Stop Talking*. Crown. See also: Helgoe, L. (2008). *Introvert Power*; Little, B. (2017). *Who Are You, Really?* (free-trait theory / restorative niches).
- **Core claim:** Introversion is a temperament associated with preference for lower-stimulation environments, deeper one-on-one engagement, and a recoverable "social energy" budget. Sustained high-stimulation networking depletes this budget; recovery (restorative niches) restores it.
- **Skill application:** Every strategy must include an explicit energy budget and recovery plan; favor depth (1:1, written, prepared) over breadth (room-working).
- **Scoring dimension link:** Energy sustainability, Authenticity fit.

### Communication accommodation & active listening
- **Anchor:** `#fw-giles-1991`
- **Citation:** Giles, H., Coupland, J., & Coupland, N. (1991). *Contexts of Accommodation*. Cambridge University Press. See also: Rogers, C. R. (1961). *On Becoming a Person* (active listening); Brown & Levinson (1987) politeness theory.
- **Core claim:** Accommodating speech rate, vocabulary, and attentiveness to a partner builds rapport without performance pressure; open-ended questions and reflective listening sustain conversation with lower self-presentation load.
- **Skill application:** Script library uses open-ended, curiosity-driven openers and reflective transitions that lower the introvert's performance burden.
- **Scoring dimension link:** Conversation readiness, Authenticity fit.

### Give-and-take reciprocity - Givers
- **Anchor:** `#fw-grant-2013`
- **Citation:** Grant, A. (2013). *Give and Take: Why Helping Others Drives Our Success*. Viking. See also: Grant, A. & Schwartz, B. (2011). Too much of a good thing.
- **Core claim:** "Giver" reciprocity styles build durable, trust-based networks; giving first (information, introductions, help) sustains relationships without self-promotion that introverts find draining or inauthentic.
- **Skill application:** Outreach and follow-up lead with concrete value to the other party; cadences include "give" touchpoints, not only "ask" touchpoints.
- **Scoring dimension link:** Follow-up consistency, Authenticity fit.

## Scoring rubric (weights fixed across the skill)

| # | Dimension | Weight | Measures | Primary framework anchor |
|---|-----------|--------|----------|--------------------------|
| 1 | Goal clarity | 0.15 | Specificity, measurability, and timeframe of the networking goal | Social capital (bonding vs bridging) |
| 2 | Energy sustainability | 0.20 | Whether the plan fits the user's social-energy budget with recovery | Introversion research (Cain) |
| 3 | Authenticity fit | 0.20 | Alignment with the user's values, voice, and comfort zones | Introversion research + Grant reciprocity |
| 4 | Conversation readiness | 0.15 | Quality and specificity of opener/transition/exit scripts | Communication accommodation & active listening |
| 5 | Follow-up consistency | 0.15 | Existence of a realistic, tiered maintenance cadence | Grant reciprocity |
| 6 | Network growth | 0.15 | Bridging-tie targeting and net-new connection plan | Granovetter weak ties |

- Each dimension is scored 0-100 with an explicit rationale and at least one citation `[anchor]` or `[assumption: ...]`.
- **Composite** = weighted sum (weights above sum to 1.00). Disclosed in every report.
- **Confidence** (0-1) = `0.4 * share_of_dimensions_with_peer_reviewed_evidence + 0.6 * (1 - degradation_penalty)`, where `degradation_penalty = 0.25` when running offline. Implemented in `tools/scoring_engine.py`.

## State-of-the-art methods & tools
- Apply the frameworks above as the scoring backbone; never score against unnamed heuristics.
- Prefer the highest available evidence tier per claim.
- Refresh trend-sensitive figures (channel popularity, response-rate norms, platform specifics) at analysis time via WebSearch; mark them `[live: YYYY-MM-DD]`.
- Use deterministic tooling (`tools/scoring_engine.py`, `tools/harness.py`) for gate enforcement, scoring math, and roadmap prioritization so results are reproducible.

## Authoritative data sources

| Source | URL | Why it matters |
|--------|-----|----------------|
| Social Networks (Elsevier) | https://www.sciencedirect.com/journal/social-networks | Peer-reviewed network/social-capital research |
| Harvard Business Review | https://hbr.org/ | Evidence-based professional-relationship articles |
| Quiet Revolution (Susan Cain) | https://www.quietrev.com/ | Introvert-strengths resources |
| American Psychological Association | https://www.apa.org/ | Research on rapport, communication, temperament |
| Adam Grant | https://adamgrant.net/ | Reciprocity and relationship research |
| arXiv (cs.SI, cs.CY) | https://arxiv.org/ | Preprints on social networks and computers & society |

## Key research references (foundational seed)

| Title | Authors | Year | Venue | Link | Anchor |
|-------|---------|------|-------|------|--------|
| The Strength of Weak Ties | Granovetter, M. S. | 1973 | American Journal of Sociology 78(6) | https://doi.org/10.1086/225469 | #fw-granovetter-1973 |
| Bowling Alone | Putnam, R. D. | 2000 | Simon & Schuster (book) | https://simonandschuster.com/books/Bowling-Alone/Robert-D-Putnam/9780743203043 | #fw-putnam-2000 |
| Structural Holes | Burt, R. S. | 1992 | Harvard University Press | https://www.hup.harvard.edu/catalog.php?isbn=9780674089155 | #fw-burt-1992 |
| Quiet: The Power of Introverts | Cain, S. | 2012 | Crown | https://www.penguinrandomhouse.com/books/308248/quiet-by-susan-cain | #fw-cain-2012 |
| Give and Take | Grant, A. | 2013 | Viking | https://www.penguinrandomhouse.com/books/307945/give-and-take-by-adam-grant | #fw-grant-2013 |
| Contexts of Accommodation | Giles, Coupland & Coupland | 1991 | Cambridge University Press | https://www.cambridge.org/9780521383912 | #fw-giles-1991 |
| Getting a Job: A Study of Contacts and Careers | Granovetter, M. | 1974/1995 | Harvard University Press | https://www.hup.harvard.edu/catalog.php?isbn=9780674354589 | #fw-granovetter-1995 |

## Analytical frameworks (used for scoring)
- Granovetter - Strength of Weak Ties
- Social capital theory (bonding vs bridging)
- Introversion research (Cain / temperament science)
- Communication accommodation & active listening
- Give-and-take reciprocity (Grant - Givers)

Scoring dimensions derived from these frameworks: Goal clarity, Energy sustainability, Authenticity fit, Conversation readiness, Follow-up consistency, Network growth.

## Self-update protocol
- **Crawl sources:** arXiv (cs.SI, cs.CY) via the arXiv API + the authoritative domain sources above.
- **Search queries:**
  - `weak ties job opportunities replication 2026`
  - `introvert networking strategy evidence`
  - `social capital career outcomes study`
  - `authentic networking reciprocity research`
- **Frequency:** weekly (cron). See `tools/knowledge_updater.py --help`.
- **Append format:** `### [YYYY-MM-DD] <title>` with Authors, Venue/Source, Key finding, Relevance score (0-1), `<!--hash:<sha256[:16] of normalized url>-->` (dedupe).
- **Dedupe:** skip entries whose URL/DOI hash already exists in the brain.
- **Quality bar:** only entries with relevance score >= 0.05 are appended; entries lacking a stable URL are logged but skipped.

## Crawled evidence
<!-- New crawled entries are appended here by tools/knowledge_updater.py. Hand-editing the hash markers breaks dedup. -->

## Knowledge update log
- **2026-06-18** - Knowledge brain v1 seeded with core frameworks, sources and crawl config for idea #198.
- **2026-07-01** - Brain upgraded to production grade: full framework definitions with citations, fixed scoring rubric and weights, evidence hierarchy, foundational reference table, anchor IDs for traceable scoring.