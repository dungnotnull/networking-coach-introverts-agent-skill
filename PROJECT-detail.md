# PROJECT-detail.md — Networking Coach for Introverts

## Executive Summary
`networking-coach-introverts` is a harness skill in the **Career, Learning & Skills** cluster (idea #198). Builds authentic, low-drain networking strategies for introverts with scripts, event tactics and relationship-maintenance systems. It executes a research-first, framework-grounded workflow that ends in a multi-dimensional score and a prioritized, effort/impact-ranked improvement roadmap.

> **Note:** Recommendations are evidence-based decision-support; validate against your specific context before acting.

## Problem Statement
Introverts find conventional networking advice draining and inauthentic. This skill designs energy-aware networking strategies, conversation scripts, and follow-up systems grounded in social-psychology research on weak ties and authentic relationship-building.

## Target Users & Use Cases
- Practitioners, learners and small teams who need an expert-grade, evidence-based analysis without hiring a specialist.
- Trigger examples:
  - "I have a 3-day conference and I'm anxious" → the skill runs its full harness and returns a scored deliverable.
  - "How do I message a stranger on LinkedIn?" → the skill runs its full harness and returns a scored deliverable.
  - "I lost touch with old contacts" → the skill runs its full harness and returns a scored deliverable.
  - "I freeze in small talk" → the skill runs its full harness and returns a scored deliverable.
  - "Networking into a new industry" → the skill runs its full harness and returns a scored deliverable.

## Harness Architecture
```
User input
   │
   ▼
[Stage 1 Intake]  sub-profile-intake
   │
   ▼
[Stage 2 Research]  SECOND-KNOWLEDGE-BRAIN.md + WebSearch/WebFetch
   │
   ▼
[Stage 3 Gate]  requirement validation
   │
   ▼
[Stage 4 Scoring]  sub-script-builder  → score vs frameworks
   │
   ▼
[Stage 5 Challenge]  devil's-advocate review
   │
   ▼
[Stage 6 Synthesis]  sub-followup-system  → scored report + roadmap
```

## Full Sub-Skill Catalog
### `sub-profile-intake`
- **Purpose:** Capture goals, energy patterns, current network, comfort zones and target contexts.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-strategy-designer`
- **Purpose:** Design an energy-aware networking strategy (channels, cadence, recovery) leveraging introvert strengths.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-script-builder`
- **Purpose:** Generate authentic conversation openers, transitions and exits for specific events.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-followup-system`
- **Purpose:** Build a lightweight relationship-maintenance/CRM cadence (weak-tie nurturing).
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-networking-roadmap`
- **Purpose:** Sequence small, repeatable actions with confidence-building milestones.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.

## Evaluation Frameworks
1. **Granovetter 'Strength of Weak Ties'** — Foundational social-capital theory on how acquaintance networks drive opportunity.
2. **Social capital theory (bonding vs bridging)** — Framework distinguishing close-network vs bridging connections and their value.
3. **Introversion research (Cain / temperament science)** — Evidence on energy management, deep one-on-one strengths and recovery needs.
4. **Communication accommodation & active listening** — Validated interpersonal techniques for rapport without performance pressure.
5. **Give-and-take reciprocity (Grant 'Givers')** — Reciprocity-based relationship building that suits low-self-promotion styles.

## Scoring Dimensions
- Goal clarity
- Energy sustainability
- Authenticity fit
- Conversation readiness
- Follow-up consistency
- Network growth

Each dimension is scored 0–100 (or 1–5) with an explicit rationale and at least one cited source or stated assumption. The composite score is a transparent weighted aggregate; weights are disclosed.

## Skill File Format Specification
- Frontmatter: `name` (= `networking-coach-introverts`), `description` (one line).
- Required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse request; classify the task and detect missing inputs (ask targeted questions).
2. Run intake sub-skill → structured profile.
3. Sync evidence from the knowledge brain; refresh via WebSearch/WebFetch when available; otherwise signal degraded mode.
4. Run the validation gate — **halt and route out** on red flags.
5. Score against frameworks; record evidence per dimension.
6. Devil's-advocate pass: challenge weakest assumptions, seek disconfirming evidence.
7. Synthesize the deliverable: scored report + prioritized roadmap (effort × impact).
8. Run quality gates; only then present output.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: ArXiv (cs.SI, cs.CY) + the authoritative domain sources listed in `CLAUDE.md`.
- Crawl config and append format are defined in `tools/knowledge_updater.py` and `SECOND-KNOWLEDGE-BRAIN.md`.

## Supporting Tools Spec — `knowledge_updater.py`
- **Inputs:** crawl query list (below), source URLs, last-run timestamp.
- **Outputs:** appended, de-duplicated, date-stamped entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- **Schedule:** weekly cron.
- **Crawl queries:** `weak ties job opportunities replication 2026`, `introvert networking strategy evidence`, `social capital career outcomes study`, `authentic networking reciprocity research`

## Quality Gates (must all pass before output)
- Every scored dimension cites a source or states an assumption.
- The applicable safety/compliance gate has passed.
- The devil's-advocate review has been performed and its objections addressed.
- The roadmap items are prioritized by effort × impact and are actionable.
- Evidence hierarchy respected (systematic review > meta-analysis > RCT/standard > expert opinion > blog).

## Test Scenarios
1. **Conference dread** — *User:* "I have a 3-day conference and I'm anxious" → *Skill:* Designs energy-budgeted plan with scripts and recovery breaks. (**Gate:** Plan includes recovery/energy budget.)
2. **Cold outreach** — *User:* "How do I message a stranger on LinkedIn?" → *Skill:* Builds authentic reciprocity-based outreach script. (**Gate:** Script avoids transactional/spam tone.)
3. **Reconnecting** — *User:* "I lost touch with old contacts" → *Skill:* Designs low-pressure weak-tie re-engagement cadence. (**Gate:** Outreach respects relationship history.)
4. **Small talk struggle** — *User:* "I freeze in small talk" → *Skill:* Provides active-listening + question frameworks. (**Gate:** Techniques cited to communication research.)
5. **Career pivot** — *User:* "Networking into a new industry" → *Skill:* Targets bridging ties and informational interviews. (**Gate:** Strategy targets bridging connections.)

## Key Design Decisions
1. Research-first: no scored claim without a citation or explicit assumption.
2. Framework-grounded: scoring uses only the named world-renowned frameworks above.
3. Composable sub-skills (≥3) with explicit gates between stages.
4. Self-improving knowledge brain via the crawl pipeline.
5. Graceful degradation when WebSearch/WebFetch are unavailable.
