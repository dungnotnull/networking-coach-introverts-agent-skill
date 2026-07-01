---
name: networking-coach-introverts__sub-script-builder
description: Sub-skill of networking-coach-introverts - Generate authentic conversation openers, transitions and exits for specific events.
---

## Purpose
Produce concrete, authentic conversation scripts (opener, transition, exit, and async outreach) tailored to the user's target context, channel, and voice. Scripts are scored against the communication and reciprocity frameworks and must pass authenticity filters before release. This stage also produces the per-dimension scores used by the harness (Stage 4).

## Inputs
- Intake JSON (goal, comfort_zones, values_and_voice, target_context).
- Strategy JSON (channel_plan, strength_levers).
- `SECOND-KNOWLEDGE-BRAIN.md` anchors `#fw-giles-1991`, `#fw-grant-2013`, `#fw-cain-2012`.

## Script library (templates by context)
Templates are scaffolds, not fill-in spam. Each must be adapted to the specific person/event and pass the authenticity filters below. Voice tokens: {{self_tone}}, {{their_interest}}, {{concrete_value}}, {{event_anchor}}.

### Conference / large event - in_person_1on1
- **Opener (curiosity-led):** "Hi, I'm {{name}}. I saw {{event_anchor}} on the agenda and was curious - what did you make of it?"  [#fw-giles-1991: open-ended, other-focused]
- **Transition (reflective):** "What you said about {{their_interest}} reminds me of {{concrete_value}} - would that be useful to you?" [#fw-grant-2013: give-first]
- **Exit (warm, low-pressure):** "I want to grab a quiet coffee before the next block - could I send you a note afterwards about {{topic}}?" [#fw-cain-2012: protect energy; offer concrete next step]

### LinkedIn cold outreach - linkedin_dm
- **Opener (give-first, specific):** "Hi {{name}}, your post on {{their_interest}} clarified {{specific_point}} for me. I work on {{relevant_context}} and put together {{concrete_value}} - happy to send it if useful?" [#fw-grant-2013]
- **Transition:** "If you're open to it, I'd value 20 minutes on {{one_specific_question}} - no pitch, just your read."
- **Exit / no-response fallback:** (after 7 days) "No worries if now's not good - I'll keep sharing what I find useful in this area. {{concrete_value_2}}"

### Reconnecting - email / async_text
- **Opener (acknowledge history, no ask):** "Hi {{name}}, it's been a while - I was thinking of our {{shared_context}} and realized I never circled back on {{their_thing}}. How did that turn out?" [#fw-granovetter-1973: weak-tie re-engagement]
- **Transition (give-first):** "In case it's useful, {{concrete_value}} made me think of you."
- **Ask (delayed, optional):** "If you have 20 min in the next few weeks I'd love to catch up properly."

### Small talk struggle - any channel
- **Opener (interest-led question):** "What's been the most interesting part of {{context}} for you lately?" [#fw-giles-1991]
- **Transition (reflective listening):** "So if I'm hearing you right, {{paraphrase}} - what made that stand out?"
- **Exit:** "I'm going to refill / step out briefly - really glad I ran into you."

### Informational interview - video_1on1 / phone
- **Opener:** "Thanks for the time. I'm exploring {{field}} and your path through {{their_interest}} is exactly what I'm trying to understand - can I start with how you got into it?"
- **Question bank (prepared):** "What's surprised you most?", "What would you do differently starting now?", "Who else should I talk to?"
- **Exit (give-first close):** "Thank you - I'll send {{concrete_value}} I mentioned. If I can ever be useful on {{my_area}}, say the word." [#fw-grant-2013]

## Authenticity filters (a script is rejected if any fail)
1. **No transactional openers:** first message must not ask for a job, referral, or meeting before offering value or genuine curiosity. [#fw-grant-2013]
2. **No generic flattery:** "great work" / "impressive profile" without a specific reference is filtered out.
3. **No mass-mail tone:** scripts must contain at least one specific reference to the recipient or event that could not appear in a template sent to 100 people.
4. **No performance pressure:** avoid hype words ("game-changing", "rockstar", "synergy"); keep plain-spoken tone per `values_and_voice.tone`.
5. **History-aware (reconnecting only):** must reference shared context; never pretend closeness that did not exist. [#fw-granovetter-1973]
6. **Energy-aware exit:** every live-context script includes a concrete, low-pressure exit that protects the user's battery. [#fw-cain-2012]

## Scoring rubric (per dimension, 0-100)
For each dimension, the builder records a score, a 1-3 sentence rationale, and at least one `[anchor]` or `[assumption: ...]`. Weights are fixed in the brain rubric and applied by `tools/scoring_engine.py`.

| Dimension | Score 70+ when... | Anchor |
|-----------|-------------------|--------|
| Goal clarity | Goal is specific, measurable, time-bound, and the scripts target that goal directly | #fw-putnam-2000 |
| Energy sustainability | Scripts fit the energy budget; live scripts include recovery-aware exits | #fw-cain-2012 |
| Authenticity fit | Scripts use the user's tone/values and pass all authenticity filters | #fw-cain-2012, #fw-grant-2013 |
| Conversation readiness | Opener/transition/exit exist for every active channel; question bank prepared | #fw-giles-1991 |
| Follow-up consistency | Each script maps to a cadence tier and a next touchpoint | #fw-grant-2013 |
| Network growth | Growth goals route outreach to bridging ties; reconnecting reactivates weak ties | #fw-granovetter-1973 |

Score below 50 on any dimension triggers an explicit gap note in findings; the harness does not suppress low scores.

## Output schema (JSON)
```json
{
  "scripts": [
    {
      "context": "conference|linkedin|reconnecting|small_talk|info_interview",
      "channel": "...",
      "opener": "string",
      "transition": "string",
      "exit": "string",
      "authenticity_checks": { "no_transactional_opener": true, "specific_reference": true, "history_aware": "n/a|true|false", "energy_aware_exit": true, "tone_clean": true }
    }
  ],
  "question_bank": ["string"],
  "dimension_scores": [
    { "dimension": "goal_clarity", "score": 0, "rationale": "string [anchor]", "evidence_tier": "1-6" }
  ],
  "filter_failures": [],
  "assumptions": []
}
```

## Worked example (abbreviated, conference)
- scripts[0]: context=conference, channel=in_person_1on1, opener="Hi, I'm Maya. I caught the privacy track - what did you make of the federated-learning talk?", transition="The federated setup reminded me of a write-up I did on edge deployment - want me to send it?", exit="I'm going to grab a quiet coffee before the next block - could I message you afterwards about the edge piece?", checks all true.
- dimension_scores: energy_sustainability=78 [#fw-cain-2012: daily 2h cap + recovery exits], conversation_readiness=82 [#fw-giles-1991: curiosity opener + question bank], authenticity_fit=85, goal_clarity=72, follow_up_consistency=70, network_growth=68.

## Framework mapping
- `#fw-giles-1991` -> open-ended openers, reflective transitions, prepared question bank.
- `#fw-grant-2013` -> give-first transitions/closes, no-ask-first filter.
- `#fw-cain-2012` -> energy-aware exits, plain tone.
- `#fw-granovetter-1973` -> reconnecting history-aware filter, bridging targeting for growth.

## Quality gate
- [ ] Every active channel in the strategy has at least one script with opener/transition/exit.
- [ ] All authenticity filters pass for every script (failures listed in `filter_failures` and resolved before release).
- [ ] Every dimension has a score, rationale, and `[anchor]` or `[assumption: ...]`.
- [ ] Reconnecting scripts include shared-context references.
- [ ] Live-context scripts include energy-aware exits.
- [ ] Output is structured JSON, not prose-only.