---
name: networking-coach-introverts__sub-followup-system
description: Sub-skill of networking-coach-introverts - Build a lightweight relationship-maintenance/CRM cadence (weak-tie nurturing).
---

## Purpose
Turn one-off conversations into a sustainable, low-drain relationship-maintenance system. Define tie tiers, a touchpoint cadence per tier, a give-first touchpoint rotation, and a re-engagement protocol for dormant weak ties. This stage feeds the roadmap and the Follow-up consistency score.

## Inputs
- Intake JSON (current_network, values_and_voice, comfort_zones).
- Strategy JSON (channel_plan, cadence model).
- `SECOND-KNOWLEDGE-BRAIN.md` anchors `#fw-granovetter-1973`, `#fw-grant-2013`, `#fw-cain-2012`.

## Tie tier model
| Tier | Size cap | Definition | Maintenance cadence | Primary channel |
|------|----------|-----------|---------------------|-----------------|
| A | <= 12 | Active mutual-value ties; you'd both pick up the phone | 1 touchpoint / 2-4 weeks (alternate give/ask) | phone, video_1on1, async_text |
| B | ~ 20-40 | Warm weak ties; met 1-3x, positive but low recent contact | 1 touchpoint / 6-8 weeks (give-led) | async_text, linkedin_dm, email |
| C | open | New/bridging ties being tested; no established mutual value yet | 1-2 outreach then evaluate; promote to B or release | linkedin_dm, async_text |

Rules:
- Tier A cap of 12 keeps maintenance feasible for low-battery users ([#fw-cain-2012]); exceeding the cap requires dropping a tie to B with a reason.
- Every cadence cycle includes >= 1 give-first touchpoint (resource, introduction, feedback) per [#fw-grant-2013]; never run an ask-only cycle.
- B and C tiers are weak-tie channels where opportunity information lives ([#fw-granovetter-1973]); do not let them go fully dormant.

## CRM record (per contact)
```json
{
  "name_or_handle": "string",
  "tier": "A|B|C",
  "context_met": "string",
  "their_interests": ["string"],
  "last_touch_date": "ISO date or null",
  "next_touch_date": "ISO date",
  "next_touch_type": "give_resource | make_intro | offer_feedback | share_update | ask_question | catch_up",
  "value_i_can_give": ["string"],
  "notes": "string"
}
```

## Touchpoint type rotation (give-heavy)
For any rolling 4-touchpoint window with a single contact, at least 2 must be give-type (`give_resource`, `make_intro`, `offer_feedback`, `share_update`). Ask-type (`ask_question`, `catch_up` with an ask) appears at most 2 of 4. This encodes Grant's giver style without degenerating into scorekeeping.

## Re-engagement protocol (dormant weak ties)
1. **Acknowledge the gap honestly** - never pretend the relationship was closer than it was ([#fw-granovetter-1973]).
2. **Lead with their world** - reference a specific recent thing they did or care about.
3. **Give first** - share one concrete resource or observation useful to them.
4. **Low-pressure close** - "No need to reply if you're swamped; just wanted this to reach you."
5. **Tier decision after reply** - promote to B if they engage; leave in C/soft-release if no reply after 2 touchpoints (do not chase).

## Cadence calendar (lightweight)
A weekly view, not a daily calendar (lower drain). Each week lists at most:
- 1-2 A-tier touchpoints
- 1-3 B-tier touchpoints
- 0-3 C-tier outreach
plus 1 give-first block. Total must respect the strategy's weekly energy budget.

## Output schema (JSON)
```json
{
  "tiers": { "A": { "cap": 12, "cadence": "1 / 2-4 wks", "members": [] }, "B": { "cadence": "1 / 6-8 wks", "members": [] }, "C": { "cadence": "outreach then evaluate", "members": [] } },
  "crm_seed": [ { "name_or_handle": "...", "tier": "...", "next_touch_date": "...", "next_touch_type": "...", "value_i_can_give": [] } ],
  "weekly_template": { "give_first_block": "string", "touches": [ { "tier": "...", "type": "...", "count_per_week": 0 } ] },
  "reengagement_script": "string",
  "follow_up_consistency_score": 0,
  "rationale": "string [anchor]",
  "assumptions": []
}
```

## Worked example (abbreviated, reconnecting trigger)
- tiers: A cap 12 (0 members yet), B (3 dormant contacts reclassified here), C (0).
- crm_seed: 3 entries, each tier B, next_touch_type=share_update then offer_feedback, value_i_can_give populated from their interests.
- weekly_template: 1 give-first block (share one resource), 1-2 B touches/week.
- reengagement_script: "Hi Sam - it's been a while since the analytics team days. I saw your move to {{company}}; the pricing work you mentioned back then came up in something I'm reading - sending it in case it's useful. No need to reply if you're swamped."
- follow_up_consistency_score: 74 [#fw-grant-2013: give-heavy rotation; #fw-granovetter-1973: weak-tie reactivation].

## Framework mapping
- `#fw-granovetter-1973` -> B/C weak-tie maintenance, re-engagement of dormant ties.
- `#fw-grant-2013` -> give-first rotation, no ask-only cycles.
- `#fw-cain-2012` -> tier-A cap, weekly (not daily) cadence, low-pressure closes.
- `#fw-putnam-2000` -> bonding (A) vs bridging (B/C) balance.

## Quality gate
- [ ] Tier A does not exceed 12 without a documented demotion.
- [ ] Every rolling 4-touchpoint window is give-heavy (>= 2 give-type).
- [ ] Re-engagement protocol is history-aware and give-first.
- [ ] Weekly touchpoint totals respect the strategy energy budget.
- [ ] Every CRM seed entry has a next_touch_date and next_touch_type.
- [ ] follow_up_consistency_score carries an `[anchor]` or `[assumption: ...]`.
- [ ] Output is structured JSON, not prose-only.