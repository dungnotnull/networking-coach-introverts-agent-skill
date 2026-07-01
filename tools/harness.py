#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harness.py - deterministic orchestration for `networking-coach-introverts`.

Wires the six harness stages (intake -> evidence -> gate -> strategy+scripts ->
devil's advocate -> synthesis) as pure functions operating on a Profile and
structured stage outputs. It enforces the gates from skills/main.md and uses
tools/scoring_engine.py for all scoring math, so results are reproducible and
auditable without calling any model, network service, or external API.

This is the production reference path: a real run composes the LLM-produced
stage JSON with this orchestrator to guarantee gate enforcement and correct
scoring. It can also be imported and unit-tested directly (see
tests/test_harness.py).

CLI:
    python tools/harness.py --demo
        Runs a built-in, fully-specified example end-to-end and prints the
        report headline. Intended for smoke-testing the pipeline wiring, not
        for producing user deliverables.

Exit codes:
    0  success (or gate held with a clarifying prompt in interactive use)
    2  validation gate failed (missing/contradictory required inputs)
    3  quality gate failed (unscored/undocumented claims or devil's-advocate gap)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Allow running both as a script and as an imported module.
try:
    from .scoring_engine import (  # type: ignore
        DIMENSIONS, WEIGHTS, Evidence, DimensionScore, RoadmapItem, Profile,
        Report, build_report, compute_energy_budget, budget_respected,
        confidence_from_tiers, composite_score, validate_dimension_scores,
        validate_gate, devil_advocate_check, prioritize_roadmap,
        detect_high_stimulation_stacking, network_growth_score,
        assemble_report_section,
    )
except ImportError:  # pragma: no cover - script invocation path
    import os
    _syspath = os.path.dirname(os.path.abspath(__file__))
    if _syspath not in sys.path:
        sys.path.insert(0, _syspath)
    from scoring_engine import (  # type: ignore
        DIMENSIONS, WEIGHTS, Evidence, DimensionScore, RoadmapItem, Profile,
        Report, build_report, compute_energy_budget, budget_respected,
        confidence_from_tiers, composite_score, validate_dimension_scores,
        validate_gate, devil_advocate_check, prioritize_roadmap,
        detect_high_stimulation_stacking, network_growth_score,
        assemble_report_section,
    )


# ---------------------------------------------------------------------------
# Stage containers (mirror the sub-skill output schemas)
# ---------------------------------------------------------------------------

@dataclass
class IntakeOutput:
    profile: Profile
    raw: Dict[str, Any]
    assumptions: List[str] = field(default_factory=list)
    degraded_mode: bool = False


@dataclass
class StrategyOutput:
    energy_budget: Dict[str, float]
    channel_hours: Dict[str, float]  # hours per week per channel
    channel_plan: List[Dict[str, Any]]
    strength_levers: List[str]
    recovery_design: List[str]
    bridging_share_pct: float
    assumptions: List[str] = field(default_factory=list)


@dataclass
class ScriptOutput:
    scripts: List[Dict[str, Any]]
    question_bank: List[str]
    dimension_scores: List[DimensionScore]
    filter_failures: List[str] = field(default_factory=list)


@dataclass
class FollowUpOutput:
    tiers: Dict[str, Any]
    crm_seed: List[Dict[str, Any]]
    weekly_template: Dict[str, Any]
    reengagement_script: str
    follow_up_consistency_score: float
    rationale: str
    assumptions: List[str] = field(default_factory=list)


@dataclass
class RoadmapOutput:
    roadmap: List[RoadmapItem]
    milestones: List[Dict[str, str]]
    network_growth_score: float
    rationale: str
    weekly_energy_check: str
    assumptions: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage functions
# ---------------------------------------------------------------------------

def run_intake(raw: Dict[str, Any]) -> Tuple[Optional[IntakeOutput], List[str]]:
    """Stage 1: build a Profile from raw intake JSON.

    Returns (output, missing_required_fields). When missing is non-empty the
    harness MUST ask clarifying questions and not proceed.
    """
    missing: List[str] = []
    goal = raw.get("goal") or {}
    energy = raw.get("energy") or {}
    comfort = raw.get("comfort_zones") or {}
    meta = raw.get("meta") or {}

    for f in ("statement", "type", "success_metric", "timeframe_weeks"):
        if not goal.get(f):
            missing.append(f"goal.{f}")
    for f in ("social_battery", "days_per_week_available", "hours_per_session_max"):
        if energy.get(f) in (None, ""):
            missing.append(f"energy.{f}")
    if not comfort.get("preferred_channels"):
        missing.append("comfort_zones.preferred_channels")
    target = raw.get("target_context") or {}
    for f in ("setting", "audience"):
        if not target.get(f):
            missing.append(f"target_context.{f}")
    if missing:
        return None, missing

    profile = Profile(
        goal_type=goal["type"],
        social_battery=energy["social_battery"],
        days_per_week_available=int(energy["days_per_week_available"]),
        hours_per_session_max=float(energy["hours_per_session_max"]),
        preferred_channels=list(comfort["preferred_channels"]),
        avoided_channels=list(comfort.get("avoided_channels") or []),
        timeframe_weeks=int(goal["timeframe_weeks"]),
        degraded_mode=bool(meta.get("degraded_mode", False)),
    )
    out = IntakeOutput(
        profile=profile,
        raw=raw,
        assumptions=list(meta.get("assumptions") or []),
        degraded_mode=profile.degraded_mode,
    )
    return out, []


def run_strategy(intake: IntakeOutput) -> StrategyOutput:
    """Stage 4a: compute the energy budget and a default channel allocation.

    The default allocation respects preferred channels and the battery-derived
    budget; a real LLM run would refine channel_plan/levers, but the budget math
    and the budget-respected invariant are enforced here regardless of source.
    """
    budget = compute_energy_budget(intake.profile)
    capacity = budget["engagement_capacity_hours"]

    # Default allocation: spread capacity across preferred channels by load so
    # weighted load <= capacity. This is a sane baseline; LLM may override.
    preferred = intake.profile.preferred_channels or ["async_text"]
    from scoring_engine import CHANNEL_LOAD_WEIGHTS  # local import keeps top clean
    per_channel_hours: Dict[str, float] = {}
    # equal raw hours per channel, then scale to fit weighted load
    raw_each = capacity / max(1, len(preferred))
    for ch in preferred:
        per_channel_hours[ch] = raw_each
    weighted = sum(per_channel_hours[ch] * CHANNEL_LOAD_WEIGHTS.get(ch, 1.0)
                   for ch in per_channel_hours)
    if weighted > capacity and weighted > 0:
        scale = capacity / weighted
        per_channel_hours = {ch: round(h * scale, 2)
                             for ch, h in per_channel_hours.items()}

    channel_plan = [
        {"channel": ch, "hours_per_week": hrs,
         "load_weight": CHANNEL_LOAD_WEIGHTS.get(ch, 1.0)}
        for ch, hrs in per_channel_hours.items()
    ]
    bridging_share = 0.65 if intake.profile.goal_type in {"job_search", "career_pivot"} else 0.45
    return StrategyOutput(
        energy_budget=budget,
        channel_hours=per_channel_hours,
        channel_plan=channel_plan,
        strength_levers=[
            "Prepared questions over improvisation [#fw-giles-1991]",
            "Depth over breadth; convert encounters to 1:1 [#fw-cain-2012]",
            "Give-first in every cadence week [#fw-grant-2013]",
        ],
        recovery_design=["Restorative block after each high-load session",
                         "No back-to-back high-load days without opt-in"],
        bridging_share_pct=round(bridging_share * 100, 1),
        assumptions=intake.assumptions,
    )


def run_scripts(strategy: StrategyOutput,
                dimension_scores: Sequence[DimensionScore],
                scripts: Sequence[Dict[str, Any]],
                question_bank: Sequence[str]) -> ScriptOutput:
    """Stage 4b: accept LLM-produced scripts + dimension scores; enforce filters.

    The dimension scores are validated by the scoring engine (range, evidence,
    weights). Filter failures are surfaced so the harness can refuse output.
    """
    failures: List[str] = []
    for sc in scripts:
        checks = sc.get("authenticity_checks") or {}
        if checks.get("no_transactional_opener") is False:
            failures.append(f"{sc.get('context')}: transactional opener")
        if checks.get("specific_reference") is False:
            failures.append(f"{sc.get('context')}: generic/no specific reference")
        if sc.get("context") == "reconnecting" and checks.get("history_aware") is False:
            failures.append("reconnecting: not history-aware")
        if checks.get("tone_clean") is False:
            failures.append(f"{sc.get('context')}: hype/performative tone")
        # live contexts need an energy-aware exit
        if sc.get("channel") in {"in_person_1on1", "small_group", "large_event",
                                 "phone", "video_1on1"}:
            if checks.get("energy_aware_exit") is False:
                failures.append(f"{sc.get('context')}: missing energy-aware exit")
    return ScriptOutput(
        scripts=list(scripts),
        question_bank=list(question_bank),
        dimension_scores=list(dimension_scores),
        filter_failures=failures,
    )


def run_followup(follow_up_consistency_score: float,
                 tiers: Dict[str, Any], crm_seed: List[Dict[str, Any]],
                 weekly_template: Dict[str, Any],
                 reengagement_script: str,
                 rationale: str,
                 assumptions: Sequence[str] = ()) -> FollowUpOutput:
    """Stage 6a: accept the follow-up system output; enforce tier-A cap."""
    a = tiers.get("A") or {}
    members = a.get("members") or []
    if len(members) > 12:
        raise ValueError(
            f"Tier A exceeds cap of 12 ({len(members)}); demote ties to B first."
        )
    return FollowUpOutput(
        tiers=tiers, crm_seed=crm_seed, weekly_template=weekly_template,
        reengagement_script=reengagement_script,
        follow_up_consistency_score=float(follow_up_consistency_score),
        rationale=rationale, assumptions=list(assumptions),
    )


def run_roadmap(items: Sequence[RoadmapItem],
                milestones: Sequence[Dict[str, str]],
                ng_components: Tuple[float, float, float],
                budget: Dict[str, float],
                rationale: str,
                assumptions: Sequence[str] = ()) -> RoadmapOutput:
    """Stage 6b: prioritize the roadmap, check stacking + budget fit."""
    prioritized = prioritize_roadmap(items)
    stacking = detect_high_stimulation_stacking(prioritized)
    ng = network_growth_score(*ng_components)
    if stacking:
        stack_note = "WARNING: high-stimulation stacking in weeks: " + ", ".join(map(str, stacking))
    else:
        stack_note = "OK: no uncontrolled high-stimulation stacking."
    # weekly load vs budget sanity (sum hours is a proxy; full per-week check
    # is done by the LLM strategy stage; we surface the budget figure).
    energy_check = (
        f"{stack_note} weekly_budget={budget['weekly_budget_session_hours']}h, "
        f"recovery_reserved={budget['recovery_reserved_hours']}h."
    )
    return RoadmapOutput(
        roadmap=prioritized, milestones=list(milestones),
        network_growth_score=ng, rationale=rationale,
        weekly_energy_check=energy_check, assumptions=list(assumptions),
    )


# ---------------------------------------------------------------------------
# Devil's advocate
# ---------------------------------------------------------------------------

DEFAULT_DEVIL_ADVOCATE_QUESTIONS: Dict[str, str] = {
    "goal_clarity": "Is the success_metric observable, or a vibe? Could the metric pass while the real goal fails?",
    "energy_sustainability": "Did we assume high motivation? Will a bad week collapse the plan? Is recovery real or just labeled?",
    "authenticity_fit": "Are we projecting an idealized voice? Would the user actually say these scripts?",
    "conversation_readiness": "Do the scripts survive a short/hostile recipient, or only the easy case?",
    "follow_up_consistency": "Is the cadence maintainable for the full timeframe, or does it decay by week 3?",
    "network_growth": "Are we over-indexing on bridging when deepening existing ties would serve better?",
}


def run_devils_advocate(responses: Dict[str, str]) -> Dict[str, str]:
    """Stage 5: ensure every dimension has an addressed objection.

    `responses` maps dimension -> 'addressed how (or score lowered by N)'.
    Missing entries are filled with the default question so the report can
    surface them; the quality gate treats unanswered (empty) entries as fails.
    """
    out: Dict[str, str] = {}
    for dim in DIMENSIONS:
        out[dim] = responses.get(dim, "").strip()
    return out


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    ok: bool
    exit_code: int
    report: Optional[Report]
    stage_outputs: Dict[str, Any]
    errors: List[str]
    clarifying_questions: List[str]


def run_pipeline(
    intake_raw: Dict[str, Any],
    scripts: Sequence[Dict[str, Any]],
    question_bank: Sequence[str],
    dimension_scores: Sequence[DimensionScore],
    followup: Dict[str, Any],
    roadmap_items: Sequence[RoadmapItem],
    milestones: Sequence[Dict[str, str]],
    ng_components: Tuple[float, float, float],
    devils_advocate: Optional[Dict[str, str]] = None,
) -> PipelineResult:
    """Run the full deterministic pipeline.

    Stage outputs (scripts, dimension_scores, followup, roadmap) are typically
    produced by the LLM sub-skills; this function enforces gates and scoring so
    no output bypasses them.
    """
    errors: List[str] = []
    clarifying: List[str] = []
    stages: Dict[str, Any] = {}

    # Stage 1 - intake
    intake, missing = run_intake(intake_raw)
    if intake is None:
        clarifying = [f"Please answer: {m}" for m in missing]
        return PipelineResult(False, 2, None, stages,
                              ["intake incomplete: " + ", ".join(missing)], clarifying)
    stages["intake"] = intake

    # Stage 3 - gate
    gate_errors = validate_gate(intake.profile)
    if gate_errors:
        return PipelineResult(False, 2, None, stages, gate_errors, clarifying)
    stages["gate_passed"] = True

    # Stage 4a - strategy
    strategy = run_strategy(intake)
    stages["strategy"] = strategy
    if not budget_respected(strategy.energy_budget, strategy.channel_hours):
        errors.append("energy budget exceeded by channel allocation")

    # Stage 4b - scripts + scoring
    script_out = run_scripts(strategy, dimension_scores, scripts, question_bank)
    stages["scripts"] = script_out
    errors.extend(script_out.filter_failures)
    score_errors = validate_dimension_scores(script_out.dimension_scores)
    errors.extend(score_errors)

    # Stage 5 - devil's advocate
    da = run_devils_advocate(devils_advocate or {})
    stages["devils_advocate"] = da
    da_missing = devil_advocate_check(da, DIMENSIONS)
    if da_missing:
        errors.append("devil's-advocate unaddressed for: " + ", ".join(da_missing))

    # Stage 6a - follow-up (tier-A cap violation is a quality-gate failure)
    try:
        fu = run_followup(
            followup.get("follow_up_consistency_score", 0.0),
            followup.get("tiers", {}), followup.get("crm_seed", []),
            followup.get("weekly_template", {}),
            followup.get("reengagement_script", ""),
            followup.get("rationale", ""),
            followup.get("assumptions", []),
        )
    except ValueError as exc:
        errors.append(str(exc))
        return PipelineResult(False, 3, None, stages, errors, clarifying)
    stages["followup"] = fu

    # Stage 6b - roadmap
    rm = run_roadmap(roadmap_items, milestones, ng_components,
                     strategy.energy_budget,
                     roadmap_items[0].rationale if roadmap_items else "",
                     followup.get("assumptions", []))
    stages["roadmap"] = rm

    if errors:
        return PipelineResult(False, 3, None, stages, errors, clarifying)

    # Build report (replaces the LLM-provided network_growth dimension score
    # with the computed one for consistency).
    final_scores: List[DimensionScore] = []
    for s in script_out.dimension_scores:
        if s.dimension == "network_growth":
            final_scores.append(dataclasses.replace(
                s, score=rm.network_growth_score,
                rationale=(s.rationale + " [computed via network_growth_score]")))
        else:
            final_scores.append(s)

    report = build_report(
        dimension_scores=final_scores,
        roadmap=rm.roadmap,
        gate_passed=True,
        devil_advocate=da,
        degraded_mode=intake.degraded_mode,
        assumptions=intake.assumptions + fu.assumptions + rm.assumptions,
    )
    stages["report"] = report
    return PipelineResult(True, 0, report, stages, [], clarifying)


# ---------------------------------------------------------------------------
# Demo (smoke-test the wiring with a fully-specified example)
# ---------------------------------------------------------------------------

def _demo() -> int:
    intake_raw = {
        "goal": {"statement": "Make useful conference connections without burning out",
                 "type": "learning", "success_metric": "5 meaningful 1:1 + 2 follow-ups",
                 "timeframe_weeks": 3, "priority": "primary"},
        "energy": {"social_battery": "low", "days_per_week_available": 3,
                   "hours_per_session_max": 2},
        "comfort_zones": {"preferred_channels": ["in_person_1on1", "async_text"],
                          "avoided_channels": ["large_event"]},
        "target_context": {"setting": "conference", "audience": "peers and seniors"},
        "meta": {"degraded_mode": False, "assumptions": []},
    }
    scripts = [{
        "context": "conference", "channel": "in_person_1on1",
        "opener": "Hi, I'm Maya. What did you make of the privacy track?",
        "transition": "That reminded me of an edge-deployment write-up - want it?",
        "exit": "Grabbing a quiet coffee - can I message you about the edge piece?",
        "authenticity_checks": {"no_transactional_opener": True,
                                "specific_reference": True,
                                "history_aware": "n/a",
                                "energy_aware_exit": True, "tone_clean": True},
    }]
    qbank = ["What's surprised you most?", "Who else should I talk to?"]
    dim_scores = [
        DimensionScore("goal_clarity", 72, "Specific 1:1 + follow-up count in 3 wks [#fw-putnam-2000]",
                       [Evidence("#fw-putnam-2000", 3)]),
        DimensionScore("energy_sustainability", 78, "Daily 2h cap + recovery exits [#fw-cain-2012]",
                       [Evidence("#fw-cain-2012", 3)]),
        DimensionScore("authenticity_fit", 85, "Curiosity-led, plain tone, give-first [#fw-grant-2013]",
                       [Evidence("#fw-grant-2013", 4), Evidence("#fw-cain-2012", 3)]),
        DimensionScore("conversation_readiness", 82, "Opener+exit+question bank [#fw-giles-1991]",
                       [Evidence("#fw-giles-1991", 3)]),
        DimensionScore("follow_up_consistency", 70, "Give-heavy B cadence [#fw-grant-2013]",
                       [Evidence("#fw-grant-2013", 4)]),
        DimensionScore("network_growth", 68, "Bridging pipeline forming [#fw-granovetter-1973]",
                       [Evidence("#fw-granovetter-1973", 2)]),
    ]
    followup = {
        "follow_up_consistency_score": 74.0,
        "tiers": {"A": {"cap": 12, "members": []},
                  "B": {"cadence": "1 / 6-8 wks", "members": []},
                  "C": {"cadence": "outreach then evaluate", "members": []}},
        "crm_seed": [], "weekly_template": {"give_first_block": "share one resource",
                                            "touches": [{"tier": "B", "type": "share_update", "count_per_week": 2}]},
        "reengagement_script": "Hi - been a while; saw your move, sending this in case useful.",
        "rationale": "give-heavy weak-tie cadence [#fw-grant-2013][#fw-granovetter-1973]",
        "assumptions": [],
    }
    roadmap_items = [
        RoadmapItem("W1-1", 1, "Send 2 give-first async touches to warm B ties",
                    "async_text", "B", 3, 1, "low", "M1",
                    "early give-first win [#fw-grant-2013]"),
        RoadmapItem("W1-2", 1, "Prepare a give asset (short field-notes write-up)",
                    "async_text", "self", 4, 2, "low", None,
                    "asset before any cold outreach [#fw-grant-2013]"),
        RoadmapItem("W2-1", 2, "Conference 1:1 conversations within 2h/day cap",
                    "in_person_1on1", "C", 5, 3, "high", "M4",
                    "depth over breadth [#fw-cain-2012]"),
        RoadmapItem("W3-1", 3, "Send 2 async follow-ups from conference contacts",
                    "async_text", "C", 4, 1, "low", None,
                    "weak-tie activation [#fw-granovetter-1973]"),
    ]
    milestones = [{"id": "M1", "trigger": "give-first touch sent", "status": "pending"},
                  {"id": "M4", "trigger": "1:1 completed", "status": "pending"}]
    ng = (0.7, 0.6, 0.75)
    da = {dim: "addressed: tested against a hostile recipient; score held"
          for dim in DIMENSIONS}

    res = run_pipeline(intake_raw, scripts, qbank, dim_scores, followup,
                       roadmap_items, milestones, ng, da)
    if not res.ok:
        print("Pipeline failed:")
        for e in res.errors:
            print("  -", e)
        return res.exit_code
    print(assemble_report_section(res.report))
    print("\nRoadmap (top 4):")
    for it in res.report.roadmap[:4]:
        print(f"  {it.id} W{it.week} pri={it.priority:.2f} {it.action}")
    print(f"\nNetwork growth: {res.stage_outputs['roadmap'].network_growth_score}")
    print(f"Energy check: {res.stage_outputs['roadmap'].weekly_energy_check}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="networking-coach-introverts harness")
    parser.add_argument("--demo", action="store_true",
                        help="run the built-in smoke-test example end-to-end")
    parser.add_argument("--input", type=str, default=None,
                        help="path to a JSON file with pipeline inputs (stage outputs)")
    args = parser.parse_args(argv)
    if args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        res = run_pipeline(
            payload["intake_raw"], payload.get("scripts", []),
            payload.get("question_bank", []), payload.get("dimension_scores", []),
            payload.get("followup", {}), payload.get("roadmap_items", []),
            payload.get("milestones", []), tuple(payload.get("ng_components", (0, 0, 0))),
            payload.get("devils_advocate"),
        )
        if not res.ok:
            print(json.dumps({"ok": False, "errors": res.errors,
                              "clarifying_questions": res.clarifying_questions}))
            return res.exit_code
        print(json.dumps({"ok": True, "composite": res.report.composite,
                          "confidence": res.report.confidence}, indent=2))
        return 0
    if args.demo:
        return _demo()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())