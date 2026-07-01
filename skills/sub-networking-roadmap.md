---
name: networking-coach-introverts__sub-networking-roadmap
description: Sub-skill of networking-coach-introverts - Sequence small, repeatable actions with confidence-building milestones.
---

## Purpose
Sequence the strategy, scripts, and follow-up system into a prioritized roadmap of small, repeatable actions ranked by impact x effort, with confidence-building milestones. This is the final synthesis stage; it produces the prioritized roadmap section of the deliverable and the Network growth score.

## Inputs
- Intake JSON (goal, timeframe_weeks).
- Strategy JSON (energy_budget, channel_plan).
- Script-builder JSON (dimension_scores).
- Follow-up JSON (tiers, weekly_template, crm_seed).
- `SECOND-KNOWLEDGE-BRAIN.md` anchors `#fw-cain-2012`, `#fw-granovetter-1973`, `#fw-grant-2013`.

## Sequencing principles
1. **Small and repeatable** - actions are sized to fit the weekly energy budget; no heroic weeks ([#fw-cain-2012]).
2. **Early wins build confidence** - week 1 contains at least one action with high confidence of success (e.g., a give-first async touch to a warm tie) before any cold outreach.
3. **Bridging late enough to be credible** - cold/bridging outreach comes after the user has prepared scripts and a give-first asset.
4. **Milestone-gated** - advancing to higher-stakes actions (cold outreach, info interviews, event attendance) requires passing a confidence milestone, not just a calendar date.
5. **Effort x impact prioritization** - roadmap items are sorted by `impact / effort` (see formula); ties broken by earlier-in-sequence and lower-stimulation.

## Effort x impact scoring
For each action:
```
impact   = 1-5 (contribution to the stated success_metric)
effort   = 1-5 (energy + time + emotional cost; 5 = very high)
priority = impact / effort   (higher = do earlier)
```
Implemented in `tools/scoring_engine.py::prioritize_roadmap`. Items are also tagged `stimulation = low|medium|high` so the scheduler never stacks two high-stimulation actions in the same week without an explicit opt-in assumption.

## Confidence milestones
| Milestone | Trigger to advance | Evidence |
|-----------|---------------------|---------|
| M1 First give-first touch sent | >= 1 async give-first touch to a warm tie completed | receipt/confirmation |
| M2 First positive reply | >= 1 reply or positive signal from B/A tier | message |
| M3 First bridging outreach | M2 passed + scripts prepared + give asset ready | sent message |
| M4 First depth conversation | >= 1 info interview / 1:1 completed | meeting occurred |
| M5 Event or ask executed | M4 passed + energy budget has recovery room | event/ask done |

Skipping a milestone is allowed only with an explicit `[assumption: user opts to skip Mx because ...]`.

## Roadmap item schema
```json
{
  "id": "W<n>-<seq>",
  "week": "integer",
  "action": "string - concrete, do-this-Tuesday",
  "channel": "...",
  "tier": "A|B|C|self",
  "impact": 1-5,
  "effort": 1-5,
  "priority": "number",
  "stimulation": "low|medium|high",
  "milestone_gate": "M0-M5 or null",
  "rationale": "string [anchor]"
}
```

## Network growth score (0-100)
```
network_growth = 40 * bridging_activation
               + 30 * new_tie_pipeline_quality
               + 30 * cadence_sustainability
```
where each component is 0-1, anchored to [#fw-granovetter-1973] (bridging), [#fw-putnam-2000] (mix), [#fw-grant-2013] (sustainability via give-first). Implemented in `tools/scoring_engine.py::network_growth_score`.

## Output schema (JSON)
```json
{
  "roadmap": [ { "id": "...", "week": 1, "action": "...", "channel": "...", "tier": "...", "impact": 0, "effort": 0, "priority": 0, "stimulation": "...", "milestone_gate": "...", "rationale": "..." } ],
  "milestones": [ { "id": "M1", "trigger": "...", "status": "pending" } ],
  "network_growth_score": 0,
  "rationale": "string [anchor]",
  "weekly_energy_check": "string - confirms roadmap fits weekly_budget",
  "assumptions": []
}
```

## Worked example (abbreviated, 6-week career-pivot roadmap)
- W1-1: Send 2 give-first async touches to warm ties (B), impact 3, effort 1, priority 3.0, stim low, gate M1 [#fw-grant-2013].
- W1-2: Prepare give asset (a short field-notes write-up), impact 4, effort 2, priority 2.0, stim low, gate null.
- W2-1: 1 info-interview request to a bridging tie, impact 5, effort 3, priority 1.67, stim medium, gate M3 [#fw-granovetter-1973].
- W3-1: Conduct info interview, impact 5, effort 4, priority 1.25, stim medium, gate M4.
- W4-1: LinkedIn bridging outreach (2), impact 4, effort 3, priority 1.33, stim medium, gate M3.
- W5-1: Add 2 new contacts to CRM tier C; schedule next touches, impact 3, effort 1, priority 3.0, stim low.
- W6-1: Review + promote/release C-tier ties; set next 6-week cycle, impact 3, effort 1, priority 3.0.
- network_growth_score: 71 [#fw-granovetter-1973 bridging pipeline active; cadence sustainable].

## Framework mapping
- `#fw-cain-2012` -> small/repeatable sizing, milestone-gating, stimulation stacking rule.
- `#fw-granovetter-1973` -> bridging activation component of the growth score; bridging outreach sequencing.
- `#fw-grant-2013` -> early give-first wins, give asset before cold outreach.
- `#fw-putnam-2000` -> cadence sustainability component.

## Quality gate
- [ ] Roadmap is sorted by priority (impact/effort) descending.
- [ ] No week contains two high-stimulation actions without an explicit opt-in assumption.
- [ ] Week 1 contains at least one high-confidence early win.
- [ ] Cold/bridging outreach is gated behind script preparation + a give asset.
- [ ] Every milestone referenced appears in `milestones`; skips carry `[assumption: ...]`.
- [ ] Roadmap totals fit the strategy's weekly energy budget (weekly_energy_check confirms).
- [ ] network_growth_score carries `[anchor]`.
- [ ] Output is structured JSON, not prose-only.