# CLAUDE.md — Networking Coach for Introverts

**Skill name:** `networking-coach-introverts`
**Source idea:** #198 (ideas.md)
**Cluster:** Career, Learning & Skills (`career-education`)
**Tagline:** Builds authentic, low-drain networking strategies for introverts with scripts, event tactics and relationship-maintenance systems.
**Current phase:** Complete - Phases 0-5 production-grade (all done)

## Problem This Skill Solves
Introverts find conventional networking advice draining and inauthentic. This skill designs energy-aware networking strategies, conversation scripts, and follow-up systems grounded in social-psychology research on weak ties and authentic relationship-building.

## Harness Flow Summary
1. **Intake** → `sub-profile-intake` gathers structured inputs.
2. **Research / evidence sync** → consult `SECOND-KNOWLEDGE-BRAIN.md`; refresh via WebSearch/WebFetch when available.
3. **Gate** → requirement validation runs before analysis.
4. **Analysis / scoring** → `sub-script-builder` scores against the named frameworks.
5. **Challenge** → devil's-advocate review stress-tests assumptions and evidence.
6. **Synthesize** → `sub-followup-system` produces the scored deliverable + prioritized roadmap.

**Quality gate:** the devil's-advocate review (`sub` quality step) MUST pass before output; every scored claim must trace to a cited source or stated assumption.

## Sub-skills
- `skills/sub-profile-intake.md` — Capture goals, energy patterns, current network, comfort zones and target contexts.
- `skills/sub-strategy-designer.md` — Design an energy-aware networking strategy (channels, cadence, recovery) leveraging introvert strengths.
- `skills/sub-script-builder.md` — Generate authentic conversation openers, transitions and exits for specific events.
- `skills/sub-followup-system.md` — Build a lightweight relationship-maintenance/CRM cadence (weak-tie nurturing).
- `skills/sub-networking-roadmap.md` — Sequence small, repeatable actions with confidence-building milestones.

## Evaluation Frameworks (world-renowned, citable)
- **Granovetter 'Strength of Weak Ties'** — Foundational social-capital theory on how acquaintance networks drive opportunity.
- **Social capital theory (bonding vs bridging)** — Framework distinguishing close-network vs bridging connections and their value.
- **Introversion research (Cain / temperament science)** — Evidence on energy management, deep one-on-one strengths and recovery needs.
- **Communication accommodation & active listening** — Validated interpersonal techniques for rapport without performance pressure.
- **Give-and-take reciprocity (Grant 'Givers')** — Reciprocity-based relationship building that suits low-self-promotion styles.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence and trend updates (graceful degradation to the knowledge brain when unavailable).
- `Read`, `Write` — load the knowledge brain; emit the deliverable.
- `Bash` — run `tools/knowledge_updater.py` (crawl4ai pipeline).

## Knowledge Sources
- **ArXiv / academic categories:** cs.SI, cs.CY
- [Social Networks journal](https://www.sciencedirect.com/journal/social-networks) — Peer-reviewed network/social-capital research.
- [Harvard Business Review networking research](https://hbr.org/) — Evidence-based professional-relationship articles.
- [Quiet Revolution (Susan Cain)](https://www.quietrev.com/) — Introvert-strengths resources.
- [APA social psychology](https://www.apa.org/) — Research on rapport and communication.
- [Adam Grant research](https://adamgrant.net/) — Reciprocity and relationship research.

## Supporting Tools
- `tools/knowledge_updater.py` — crawl4ai + WebSearch pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (recommended weekly cron).

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Define frameworks, sub-skills and scoring dimensions
- [x] Author knowledge brain v1 and crawl pipeline
- [x] Expand knowledge brain via first scheduled crawl (code-ready; live crawl deferred to production runtime)
- [x] Add adversarial/edge-case test scenarios (14 scenarios + 36 unittest cases)

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — living domain knowledge base
