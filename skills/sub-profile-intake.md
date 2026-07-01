---
name: networking-coach-introverts__sub-profile-intake
description: Sub-skill of networking-coach-introverts - Capture goals, energy patterns, current network, comfort zones and target contexts.
---

## Purpose
Capture a complete, structured profile of the user's networking goal, social-energy patterns, current network shape, comfort zones, and target context. This is Stage 1 of the harness. The profile is the single source of truth consumed by every downstream stage, so completeness here prevents compounding errors.

## Required input schema (JSON)
The intake output MUST conform to this schema. Missing required fields trigger targeted clarifying questions rather than assumptions.

```json
{
  "goal": {
    "statement": "string - what the user wants from networking, in their words",
    "type": "job_search | career_pivot | client_work | learning | community | reconnecting | other",
    "success_metric": "string - observable, e.g. '3 informational interviews in 6 weeks'",
    "timeframe_weeks": "integer >= 1",
    "priority": "primary | secondary"
  },
  "energy": {
    "social_battery": "high | medium | low",
    "peak_windows": ["string - e.g. 'mornings', 'early afternoons'"],
    "recovery_activities": ["string"],
    "days_per_week_available": "integer 0-7",
    "hours_per_session_max": "number > 0"
  },
  "current_network": {
    "bonding_strength": "high | medium | low",
    "bridging_strength": "high | medium | low",
    "contacts_estimate": "integer",
    "dormant_contacts_to_reconnect": ["string - names or descriptions"]
  },
  "comfort_zones": {
    "preferred_channels": ["async_text | email | linkedin_dm | phone | video | in_person_1on1 | small_group | large_event"],
    "avoided_channels": ["same vocabulary"],
    "strengths": ["string - e.g. 'deep listening', 'written clarity', 'preparation'"],
    "discomforts": ["string - e.g. 'cold opens', 'self-promotion', 'group dinners'"]
  },
  "target_context": {
    "setting": "conference | linkedin | email | industry_community | workplace | alumni | other",
    "audience": "string - who they need to reach",
    "constraints": ["string - e.g. 'no travel budget', 'must stay anonymous until ready'"],
    "timeline_event_date": "ISO date or null"
  },
  "values_and_voice": {
    "values": ["string - e.g. 'reciprocity', 'honesty', 'low-self-promotion'"],
    "tone": "string - e.g. 'warm, plain-spoken, no hype'"
  },
  "meta": {
    "degraded_mode": false,
    "assumptions": []
  }
}
```

## Field reference
- **goal.type** drives framework emphasis: `job_search`/`career_pivot` -> Granovetter weak ties + bridging; `reconnecting` -> weak-tie re-engagement + Grant reciprocity; `learning`/`community` -> bonding+bridging balance.
- **energy.social_battery** sets the starting energy budget multiplier: high=1.0, medium=0.6, low=0.35 (used by `sub-strategy-designer`).
- **comfort_zones.preferred_channels** and **avoided_channels** use the fixed channel vocabulary so downstream stages can route scripts to the right channel.
- **target_context.timeline_event_date** triggers conference/event-specific energy budgeting when present.
- **meta.degraded_mode** is false unless WebSearch/WebFetch are unavailable at intake time; never silently true.

## Intake question bank (mapped to triggers)
Ask the minimum set needed to fill missing required fields. Use plain language; do not expose field names.

| Missing field | Question |
|---------------|----------|
| goal.statement + goal.type | "What do you most want out of networking in the next few months?" |
| goal.success_metric | "How will you know it worked? Give me something you could count or point to." |
| goal.timeframe_weeks | "Over how many weeks?" |
| energy.social_battery | "After a 2-hour social event, are you wiped out, tired but okay, or still energized?" |
| energy.days_per_week_available + hours_per_session_max | "How many days a week and how many hours per session can you realistically give this?" |
| current_network.bridging_strength | "How many of your contacts are in different companies, fields, or circles than your usual one?" |
| comfort_zones.preferred_channels | "Which ways of reaching out feel least draining - written messages, 1:1 calls, small groups, events?" |
| comfort_zones.discomforts | "What specifically makes networking hard for you?" |
| target_context.audience + setting | "Who do you need to reach, and where do they show up?" |
| values_and_voice.values | "What would make this feel authentic versus like performing?" |

## Procedure
1. Parse the user's request; classify `goal.type` and `target_context.setting` from language cues.
2. Fill every field you can from explicit statements; for each remaining required field, ask exactly the mapped question. Batch unanswered questions (max 3 at once) to limit drain.
3. Normalize free text into the controlled vocabularies above (channels, types, battery levels). Record the user's verbatim phrasing in the relevant `statement`/`tone` fields so voice is preserved.
4. Estimate `current_network.bonding_strength` vs `bridging_strength` from the user's description; mark as `[assumption: inferred from description]` if not directly stated.
5. Set `meta.degraded_mode` based on tool availability at this moment.
6. Emit the structured JSON record as the stage output (no prose-only answers).

## Output
A JSON record conforming to the schema above, plus a one-line intake summary: "Intake complete: goal=<type>, battery=<level>, bridging=<strength>, channels=<top 2 preferred>."

## Worked example (abbreviated)
Trigger: "I have a 3-day conference and I'm anxious."
```json
{
  "goal": { "statement": "Make useful connections at the conference without burning out", "type": "learning", "success_metric": "5 meaningful 1:1 conversations + 2 follow-ups agreed", "timeframe_weeks": 3, "priority": "primary" },
  "energy": { "social_battery": "low", "peak_windows": ["mornings"], "recovery_activities": ["solo lunch", "walks", "quiet evenings"], "days_per_week_available": 3, "hours_per_session_max": 2 },
  "current_network": { "bonding_strength": "medium", "bridging_strength": "low", "contacts_estimate": 25, "dormant_contacts_to_reconnect": [] },
  "comfort_zones": { "preferred_channels": ["in_person_1on1", "async_text"], "avoided_channels": ["large_event", "small_group"], "strengths": ["deep listening", "preparation"], "discomforts": ["cold opens", "group dinners"] },
  "target_context": { "setting": "conference", "audience": "peers and a few senior practitioners in my field", "constraints": ["3-day format is draining"], "timeline_event_date": "2026-09-15" },
  "values_and_voice": { "values": ["reciprocity", "honesty", "low-self-promotion"], "tone": "warm, plain-spoken, curious" },
  "meta": { "degraded_mode": false, "assumptions": ["[assumption: bridging_strength inferred from 'I mostly know people at my own company']"] }
}
```

## Framework mapping
- Granovetter `#fw-granovetter-1973` -> `current_network.bridging_strength`, `goal.type=job_search|career_pivot`.
- Social capital `#fw-putnam-2000` -> bonding/bridging diagnosis.
- Introversion `#fw-cain-2012` -> `energy.*`, recovery activities, comfort zones.
- Communication `#fw-giles-1991` -> `comfort_zones.strengths` (listening, written clarity).
- Grant reciprocity `#fw-grant-2013` -> `values_and_voice.values` when reciprocity named.

## Quality gate (must pass before handing off)
- [ ] Every required field in the schema is populated or its missing value is represented by a targeted question already asked.
- [ ] Controlled-vocabulary fields use only allowed values.
- [ ] At least one explicit `[assumption: ...]` marks any inferred (not user-stated) field.
- [ ] `meta.degraded_mode` is set truthfully.
- [ ] Output is the structured JSON record (not prose).