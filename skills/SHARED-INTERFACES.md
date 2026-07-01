# skills/SHARED-INTERFACES.md - Cross-Skill Reuse (career-education cluster)

> Phase 5 deliverable for `networking-coach-introverts`. Documents the reusable interfaces that sibling skills in the **Career, Learning & Skills** (`career-education`) cluster can import so intake, scoring, and roadmap patterns are shared rather than re-implemented.

## Why share
Several harness skills in the cluster share the same backbone: structured intake -> evidence-sync -> gate -> framework-scored analysis -> devil's advocate -> prioritized roadmap. Reusing the contracts below keeps scores comparable across skills, avoids divergent gate logic, and lets a single deterministic engine (`tools/scoring_engine.py`) serve multiple skills.

## Shared assets (this skill exports)
1. **Scoring engine** - `tools/scoring_engine.py`
   - Fixed-weight composite scoring, evidence-tier confidence, dimension validation, roadmap prioritization (impact/effort), high-stimulation stacking detection, gate validation, devil's-advocate presence check.
   - Skill-agnostic: a sibling skill defines its own `DIMENSIONS`/`WEIGHTS` and reuses the math functions (`composite_score`, `confidence_from_tiers`, `prioritize_roadmap`, `validate_gate`, `devil_advocate_check`).
2. **Harness orchestrator pattern** - `tools/harness.py`
   - Stage functions (`run_intake`, `run_strategy`, `run_scripts`, `run_followup`, `run_roadmap`, `run_devils_advocate`) and `run_pipeline` with exit codes 0/2/3. Sibling skills mirror this shape with their own stage logic but keep the gate/exit-code contract.
3. **Intake schema convention** - the JSON shape in `skills/sub-profile-intake.md` (`goal`, `energy`, `current_network`, `comfort_zones`, `target_context`, `values_and_voice`, `meta`). Sibling skills add skill-specific sub-objects but keep `meta.degraded_mode` and `meta.assumptions` identical.
4. **Roadmap item schema** - `tools/scoring_engine.py::RoadmapItem` (`id, week, action, channel, tier, impact, effort, stimulation, milestone_gate, rationale`) and the `impact/effort` priority convention.

## Import contract for sibling skills
A sibling skill (e.g. a "career-pivot-planner" or "learning-path-architect" skill) reuses this skill's engine by:

1. Copying or vendoring `tools/scoring_engine.py` into its own `tools/` directory (no runtime dependency on this repo).
2. Defining its own `DIMENSIONS` and `WEIGHTS` (weights must sum to 1.0) and its own framework anchors in its knowledge brain.
3. Calling the shared functions:
   ```python
   from scoring_engine import (
       composite_score, confidence_from_tiers, validate_dimension_scores,
       prioritize_roadmap, detect_high_stimulation_stacking,
       validate_gate, devil_advocate_check, build_report,
       DimensionScore, Evidence, RoadmapItem, Profile, Report,
   )
   ```
4. Mirroring the gate/exit-code contract (0 = ok, 2 = validation gate failed, 3 = quality gate failed) so cluster-wide orchestration is uniform.

## Shared interface summary (stable contracts)

| Interface | Location | Stability | Notes |
|-----------|----------|-----------|-------|
| `composite_score(scores)` | scoring_engine | stable | weights fixed per skill |
| `confidence_from_tiers(scores, degraded_mode)` | scoring_engine | stable | tier<=3 = peer-reviewed |
| `validate_gate(profile)` | scoring_engine | stable | red-flag list |
| `devil_advocate_check(objections, dims)` | scoring_engine | stable | per-dimension presence |
| `prioritize_roadmap(items)` | scoring_engine | stable | impact/effort desc |
| `RoadmapItem` schema | scoring_engine | stable | impact/effort 1..5 |
| Intake JSON shape | sub-profile-intake.md | stable | `meta.degraded_mode`, `meta.assumptions` reserved |
| Pipeline exit codes | harness.py | stable | 0 / 2 / 3 |

## Versioning
- These contracts are **stable** (semver: additions allowed; no breaking changes to function signatures or the roadmap/intake schemas without a major version bump noted here).
- Skill-specific dimensions and anchors are NOT shared; only the engine math and schemas are.

## Example: sibling skill reuse
```python
# In a sibling skill's own tools/scoring_engine.py (vendored copy) it defines:
DIMENSIONS = ("goal_clarity", "skill_gap", "roi", "risk", "plan_quality", "sustainability")
WEIGHTS = {"goal_clarity": 0.20, "skill_gap": 0.20, "roi": 0.20,
           "risk": 0.15, "plan_quality": 0.15, "sustainability": 0.10}
# then reuses composite_score, confidence_from_tiers, prioritize_roadmap, validate_gate,
# devil_advocate_check unchanged - only the dimension names and weights differ.
```

## Quality gate for reuse
- [ ] Sibling skill weights sum to 1.0.
- [ ] Sibling skill reuses the exit-code contract (0/2/3).
- [ ] Sibling skill preserves `meta.degraded_mode` and `meta.assumptions` in its intake schema.
- [ ] Sibling skill reuses `RoadmapItem` and the `impact/effort` priority convention.
- [ ] No sibling skill bypasses `validate_gate` or `devil_advocate_check`.