---
name: networking-coach-introverts__sub-strategy-designer
description: Sub-skill of networking-coach-introverts - Design an energy-aware networking strategy (channels, cadence, recovery) leveraging introvert strengths.
---

## Purpose
Translate the intake profile into an energy-aware networking strategy: which channels to use, how often, how to recover, and how to lean into introvert strengths (depth, preparation, listening). Output is a structured record consumed by the script builder and roadmap stages.

## Inputs
- The Stage 1 intake JSON (`sub-profile-intake` output).
- Relevant entries from `SECOND-KNOWLEDGE-BRAIN.md` (anchors `#fw-cain-2012`, `#fw-granovetter-1973`, `#fw-putnam-2000`, `#fw-grant-2013`).

## Channel taxonomy (controlled vocabulary)
| Channel | Stimulation load | Introvert fit | Best for |
|---------|------------------|---------------|----------|
| async_text / email | low | high | Prepared outreach, follow-ups, value-giving |
| linkedin_dm | low | high | Bridging outreach to weak ties |
| phone | medium | medium | Reconnecting, warmth without travel |
| video_1on1 | medium | medium | Informational interviews, depth |
| in_person_1on1 | medium-high | high (controlled) | Depth, trust, conferences (1:1 offshoots) |
| small_group | high | medium | Curated dinners, affinity meetups |
| large_event | very high | low (needs budgeting) | Conferences, mixers - use sparingly |

## Energy-budget model
Compute a weekly energy budget in "session-hours" (a session-hour = 1 hour of active social engagement for a medium-battery person).

```
base_hours = days_per_week_available * hours_per_session_max
battery_multiplier = {high: 1.0, medium: 0.6, low: 0.35}[social_battery]
weekly_budget = base_hours * battery_multiplier
```

Then allocate across channels by load. Channel load weights: async_text/email/linkedin_dm = 0.5, phone/video_1on1/in_person_1on1 = 1.0, small_group = 1.5, large_event = 2.0. Sum of (channel_hours * load) must stay <= weekly_budget. Always reserve >= 20% of weekly_budget for recovery (do not allocate recovery to engagement).

Implemented in `tools/harness.py::compute_energy_budget`.

## Cadence model (touchpoints per week by tie tier)
| Tier | Definition | Async touchpoints/wk | Sync touchpoints/wk |
|------|-----------|----------------------|---------------------|
| A | Active mutual-value ties (<=12) | 0-1 | 0-1 |
| B | Warm weak ties (~20-40) | 1-2 | 0-1 / 2 wks |
| C | Bridging / new ties being tested | 1-3 outreach | 0-1 / 2 wks (info interviews) |

Cadence is capped so total engagement stays within the weekly energy budget; if it exceeds, reduce C-tier outreach first, then B sync.

## Introvert-strength leveraging
- **Preparation over improvisation:** pre-research targets; enter with 2-3 prepared questions (`#fw-giles-1991`).
- **Depth over breadth:** prefer 1:1 and small curated settings; convert event encounters into 1:1 follow-ups (`#fw-cain-2012`).
- **Written-first:** lead outreach async where possible; use written clarity as a strength.
- **Give-first:** every cadence week includes at least one "give" touchpoint (share a resource, make an introduction, offer feedback) (`#fw-grant-2013`).
- **Bridging focus for growth goals:** when `goal.type` in {job_search, career_pivot}, route >= 60% of C-tier outreach to bridging ties (`#fw-granovetter-1973`).

## Recovery design
- Block one restorative activity immediately after any high-load session (large_event, small_group).
- For multi-day events (conference), cap active engagement at 2 session-hours/day and schedule a daily recovery block; one "light day" mid-event if >= 3 days.
- No two high-load days back-to-back unless the user explicitly opts in (record as `[assumption: user opted into back-to-back high-load]`).

## Output schema (JSON)
```json
{
  "energy_budget": {
    "weekly_budget_session_hours": "number",
    "battery_multiplier": "number",
    "engagement_allocation": [{ "channel": "...", "hours_per_week": 0, "load_weight": 0 }],
    "recovery_reserved_hours": "number",
    "recovery_blocks": ["string"]
  },
  "channel_plan": [{ "tier": "A|B|C", "channel": "...", "cadence_per_week": 0, "rationale": "string [anchor]" }],
  "strength_levers": ["string [anchor]"],
  "recovery_design": ["string"],
  "bridging_share_pct": "number 0-100",
  "assumptions": []
}
```

## Worked example (abbreviated, from the conference intake)
- weekly_budget = 3 days * 2h * 0.35 = 2.1 session-hours/week (training weeks); event week uses daily cap of 2 active hours/day.
- channel_plan: C-tier linkedin_dm outreach before event (2/wk, load 0.5 -> 1.0 budget unit); in_person_1on1 at event (2h/day, load 1.0 -> 2.0 units/day, within daily cap); async_text follow-ups after.
- bridging_share_pct = 70 (learning goal but user named senior practitioners outside current circle).
- recovery_design: solo lunch + walk after each session block; light Day 2; quiet evenings all 3 days.
- strength_levers: "Pre-research 5 attendees; bring 2 prepared questions each [#fw-giles-1991]", "Convert each good encounter into a 1:1 coffee slot [#fw-cain-2012]", "Give-first: share one relevant resource in each first follow-up [#fw-grant-2013]".

## Framework mapping
- `#fw-cain-2012` -> energy budget, recovery, depth-over-breadth.
- `#fw-granovetter-1973` -> bridging share for growth goals.
- `#fw-putnam-2000` -> bonding/bridging balance in tier definitions.
- `#fw-grant-2013` -> give-first cadence rule.
- `#fw-giles-1991` -> preparation and question-led engagement.

## Quality gate
- [ ] weekly_budget computed and not exceeded by the sum of weighted engagement.
- [ ] Recovery reserves >= 20% of weekly_budget and is non-empty.
- [ ] channel_plan respects the user's avoided_channels (no forced use of avoided channels without an explicit opt-in assumption).
- [ ] At least one give-first touchpoint is scheduled per cadence week.
- [ ] bridging_share_pct set and >= 60% when goal.type is a growth type.
- [ ] Every lever and material claim carries an `[anchor]` or `[assumption: ...]`.
- [ ] Output is structured JSON, not prose-only.