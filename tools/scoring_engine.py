#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scoring_engine.py - deterministic scoring for `networking-coach-introverts`.

This module encodes the fixed scoring rubric, weights, composite/confidence
math, gate validation, devil's-advocate presence check, and roadmap
prioritization defined in SECOND-KNOWLEDGE-BRAIN.md and skills/main.md.

It is intentionally dependency-free (Python 3.9+ standard library only) so the
harness results are reproducible and auditable. It does NOT call any model,
network service, or external API; all inputs are passed in as plain data.

Public API:
    DIMENSIONS, WEIGHTS, composite_score, confidence_from_tiers,
    validate_dimension_scores, prioritize_roadmap, network_growth_score,
    devil_advocate_check, assemble_report_section, Evidence, DimensionScore,
    RoadmapItem, Profile, Report.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Fixed rubric (mirrors SECOND-KNOWLEDGE-BRAIN.md). Never mutate at runtime.
# ---------------------------------------------------------------------------

DIMENSIONS: Tuple[str, ...] = (
    "goal_clarity",
    "energy_sustainability",
    "authenticity_fit",
    "conversation_readiness",
    "follow_up_consistency",
    "network_growth",
)

WEIGHTS: Dict[str, float] = {
    "goal_clarity": 0.15,
    "energy_sustainability": 0.20,
    "authenticity_fit": 0.20,
    "conversation_readiness": 0.15,
    "follow_up_consistency": 0.15,
    "network_growth": 0.15,
}

# Evidence tiers from the brain (1 = highest, 6 = assumption).
EVIDENCE_TIERS: Tuple[str, ...] = (
    "systematic_review_or_meta",
    "peer_reviewed_primary",
    "peer_reviewed_theory",
    "expert_practitioner",
    "reputable_blog",
    "assumption",
)

DEGRADATION_PENALTY = 0.25  # applied to confidence when running offline
CHANNEL_LOAD_WEIGHTS: Dict[str, float] = {
    "async_text": 0.5,
    "email": 0.5,
    "linkedin_dm": 0.5,
    "phone": 1.0,
    "video_1on1": 1.0,
    "in_person_1on1": 1.0,
    "small_group": 1.5,
    "large_event": 2.0,
}
BATTERY_MULTIPLIER = {"high": 1.0, "medium": 0.6, "low": 0.35}
RECOVERY_RESERVE_FRACTION = 0.20


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Evidence:
    """A single piece of evidence backing a scored claim."""
    anchor: str
    tier: int  # 1..6 per EVIDENCE_TIERS (1 highest)
    citation: str = ""
    assumption: Optional[str] = None  # set when tier == 6

    @property
    def is_assumption(self) -> bool:
        return self.tier == 6 or self.assumption is not None


@dataclass
class DimensionScore:
    dimension: str
    score: float  # 0..100
    rationale: str
    evidence: List[Evidence] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.dimension not in WEIGHTS:
            raise ValueError(f"Unknown dimension: {self.dimension}")
        if not (0.0 <= self.score <= 100.0):
            raise ValueError(
                f"{self.dimension} score {self.score} out of range 0..100"
            )
        if not self.evidence:
            raise ValueError(
                f"{self.dimension} has no evidence; every score needs an anchor "
                "or an explicit assumption"
            )
        if not any(e.is_assumption for e in self.evidence) and not any(
            e.anchor for e in self.evidence
        ):
            raise ValueError(f"{self.dimension} evidence lacks anchors/assumptions")


@dataclass
class RoadmapItem:
    id: str
    week: int
    action: str
    channel: str
    tier: str  # A|B|C|self
    impact: int  # 1..5
    effort: int  # 1..5
    stimulation: str = "low"  # low|medium|high
    milestone_gate: Optional[str] = None
    rationale: str = ""

    def __post_init__(self) -> None:
        if not (1 <= self.impact <= 5):
            raise ValueError(f"impact must be 1..5, got {self.impact}")
        if not (1 <= self.effort <= 5):
            raise ValueError(f"effort must be 1..5, got {self.effort}")
        if self.stimulation not in {"low", "medium", "high"}:
            raise ValueError(f"bad stimulation: {self.stimulation}")
        if self.tier not in {"A", "B", "C", "self"}:
            raise ValueError(f"bad tier: {self.tier}")

    @property
    def priority(self) -> float:
        return self.impact / self.effort


@dataclass
class Profile:
    """Minimal projection of the intake profile used by the engine."""
    goal_type: str
    social_battery: str
    days_per_week_available: int
    hours_per_session_max: float
    preferred_channels: List[str]
    avoided_channels: List[str]
    timeframe_weeks: int
    degraded_mode: bool = False


@dataclass
class Report:
    composite: float
    confidence: float
    dimension_scores: List[DimensionScore]
    roadmap: List[RoadmapItem]
    gate_passed: bool
    devil_advocate: Dict[str, str]
    degraded_mode: bool
    assumptions: List[str]


# ---------------------------------------------------------------------------
# Scoring math
# ---------------------------------------------------------------------------

def composite_score(scores: Sequence[DimensionScore]) -> float:
    """Weighted sum of dimension scores (0..100). Weights are fixed and sum to 1."""
    if len(scores) != len(DIMENSIONS):
        raise ValueError(
            f"expected {len(DIMENSIONS)} dimension scores, got {len(scores)}"
        )
    seen = {s.dimension for s in scores}
    if seen != set(DIMENSIONS):
        missing = set(DIMENSIONS) - seen
        raise ValueError(f"missing dimensions: {sorted(missing)}")
    total = 0.0
    for s in scores:
        total += WEIGHTS[s.dimension] * s.score
    return round(total, 2)


def confidence_from_tiers(scores: Sequence[DimensionScore], degraded_mode: bool) -> float:
    """Confidence in [0,1] from evidence tiers + degradation penalty.

    confidence = 0.4 * share_of_dimensions_with_peer_reviewed_evidence
               + 0.6 * (1 - degradation_penalty)
    Peer-reviewed = tier <= 3 (systematic review, primary study, theory paper).
    """
    peer = 0
    for s in scores:
        if any(e.tier <= 3 and not e.is_assumption for e in s.evidence):
            peer += 1
    share = peer / max(1, len(scores))
    penalty = DEGRADATION_PENALTY if degraded_mode else 0.0
    conf = 0.4 * share + 0.6 * (1.0 - penalty)
    return round(max(0.0, min(1.0, conf)), 3)


def validate_dimension_scores(scores: Sequence[DimensionScore]) -> List[str]:
    """Return a list of gate violations; empty list means pass."""
    errors: List[str] = []
    try:
        composite_score(scores)  # raises on missing/extra dimensions
    except ValueError as e:
        errors.append(str(e))
    for s in scores:
        for e in s.evidence:
            if not (1 <= e.tier <= 6):
                errors.append(f"{s.dimension}: evidence tier {e.tier} out of 1..6")
            if e.is_assumption and not e.assumption:
                errors.append(
                    f"{s.dimension}: assumption evidence must state the assumption"
                )
    return errors


# ---------------------------------------------------------------------------
# Energy budget (mirrors sub-strategy-designer)
# ---------------------------------------------------------------------------

def compute_energy_budget(profile: Profile) -> Dict[str, float]:
    """Return weekly session-hour budget and recovery reserve.

    weekly_budget = days_per_week * hours_per_session * battery_multiplier
    recovery_reserved = max(0.5, RECOVERY_RESERVE_FRACTION * weekly_budget)
    """
    if profile.social_battery not in BATTERY_MULTIPLIER:
        raise ValueError(f"bad social_battery: {profile.social_battery}")
    mult = BATTERY_MULTIPLIER[profile.social_battery]
    weekly_budget = profile.days_per_week_available * profile.hours_per_session_max * mult
    recovery = max(0.5, RECOVERY_RESERVE_FRACTION * weekly_budget)
    return {
        "weekly_budget_session_hours": round(weekly_budget, 2),
        "battery_multiplier": mult,
        "recovery_reserved_hours": round(recovery, 2),
        "engagement_capacity_hours": round(max(0.0, weekly_budget - recovery), 2),
    }


def engagement_load_hours(channel_hours: Dict[str, float]) -> float:
    """Weighted load: sum(channel_hours * load_weight)."""
    total = 0.0
    for ch, hrs in channel_hours.items():
        if ch not in CHANNEL_LOAD_WEIGHTS:
            raise ValueError(f"unknown channel: {ch}")
        total += hrs * CHANNEL_LOAD_WEIGHTS[ch]
    return round(total, 2)


def budget_respected(budget: Dict[str, float], channel_hours: Dict[str, float]) -> bool:
    """True when weighted engagement load fits within engagement capacity."""
    return engagement_load_hours(channel_hours) <= budget["engagement_capacity_hours"]


# ---------------------------------------------------------------------------
# Roadmap prioritization (mirrors sub-networking-roadmap)
# ---------------------------------------------------------------------------

def prioritize_roadmap(items: Sequence[RoadmapItem]) -> List[RoadmapItem]:
    """Sort by priority (impact/effort) descending; tie-break by week then stimulation."""
    stim_rank = {"low": 0, "medium": 1, "high": 2}
    return sorted(
        items,
        key=lambda it: (-it.priority, it.week, stim_rank[it.stimulation], it.id),
    )


def detect_high_stimulation_stacking(items: Sequence[RoadmapItem]) -> List[int]:
    """Return weeks that contain >1 high-stimulation action (a stacking violation)."""
    by_week: Dict[int, int] = {}
    for it in items:
        if it.stimulation == "high":
            by_week[it.week] = by_week.get(it.week, 0) + 1
    return sorted(w for w, c in by_week.items() if c > 1)


def network_growth_score(
    bridging_activation: float,
    new_tie_pipeline_quality: float,
    cadence_sustainability: float,
) -> float:
    """0..100 network-growth score (components each in [0,1])."""
    for name, val in (
        ("bridging_activation", bridging_activation),
        ("new_tie_pipeline_quality", new_tie_pipeline_quality),
        ("cadence_sustainability", cadence_sustainability),
    ):
        if not (0.0 <= val <= 1.0):
            raise ValueError(f"{name} must be in [0,1], got {val}")
    raw = 40 * bridging_activation + 30 * new_tie_pipeline_quality + 30 * cadence_sustainability
    return round(raw, 2)


# ---------------------------------------------------------------------------
# Gate + devil's advocate (mirrors skills/main.md Stage 3 & 5)
# ---------------------------------------------------------------------------

REQUIRED_PROFILE_FIELDS = (
    "goal_type",
    "social_battery",
    "days_per_week_available",
    "hours_per_session_max",
    "preferred_channels",
    "timeframe_weeks",
)

BATTERY_VALUES = {"high", "medium", "low"}
GOAL_GROWTH_TYPES = {"job_search", "career_pivot"}


def validate_gate(profile: Profile) -> List[str]:
    """Return red-flag violations; empty list means gate passes."""
    errors: List[str] = []
    if profile.social_battery not in BATTERY_VALUES:
        errors.append(f"invalid social_battery: {profile.social_battery}")
    if profile.timeframe_weeks < 1:
        errors.append("timeframe_weeks must be >= 1")
    if profile.hours_per_session_max <= 0:
        errors.append("hours_per_session_max must be > 0")
    if profile.days_per_week_available < 0 or profile.days_per_week_available > 7:
        errors.append("days_per_week_available must be 0..7")
    if not profile.preferred_channels:
        errors.append("preferred_channels must be non-empty")
    if profile.preferred_channels and profile.avoided_channels:
        if set(profile.preferred_channels) == set(profile.avoided_channels):
            errors.append("preferred and avoided channels are identical (contradictory)")
    return errors


def devil_advocate_check(objections: Dict[str, str], dimension_names: Sequence[str]) -> List[str]:
    """Every dimension must have an objection addressed (or marked 'accepted').

    Returns a list of missing/unaddressed dimensions. Empty list = pass.
    """
    missing: List[str] = []
    for dim in dimension_names:
        note = objections.get(dim)
        if not note or not note.strip():
            missing.append(dim)
    return missing


# ---------------------------------------------------------------------------
# Report assembly helpers
# ---------------------------------------------------------------------------

def assemble_report_section(report: Report) -> str:
    """Render the dimension-score + headline section as markdown (no full report)."""
    lines = [
        f"**Composite score:** {report.composite} / 100",
        f"**Confidence:** {report.confidence}",
    ]
    if report.degraded_mode:
        lines.append("**Mode:** degraded (offline-knowledge) - trend-sensitive facts not refreshed.")
    lines.append("")
    lines.append("| Dimension | Score | Weight | Rationale | Evidence |")
    lines.append("|-----------|-------|--------|-----------|----------|")
    for s in report.dimension_scores:
        ev = "; ".join(
            f"[assumption: {e.assumption}]" if e.is_assumption else f"[{e.anchor} t{e.tier}]"
            for e in s.evidence
        )
        lines.append(
            f"| {s.dimension} | {s.score} | {WEIGHTS[s.dimension]} | {s.rationale} | {ev} |"
        )
    return "\n".join(lines)


def build_report(
    dimension_scores: Sequence[DimensionScore],
    roadmap: Sequence[RoadmapItem],
    gate_passed: bool,
    devil_advocate: Dict[str, str],
    degraded_mode: bool,
    assumptions: Optional[List[str]] = None,
) -> Report:
    """Construct a Report, computing composite + confidence from the rubric."""
    return Report(
        composite=composite_score(dimension_scores),
        confidence=confidence_from_tiers(dimension_scores, degraded_mode),
        dimension_scores=list(dimension_scores),
        roadmap=prioritize_roadmap(roadmap),
        gate_passed=gate_passed,
        devil_advocate=dict(devil_advocate),
        degraded_mode=degraded_mode,
        assumptions=list(assumptions or []),
    )


__all__ = [
    "DIMENSIONS", "WEIGHTS", "EVIDENCE_TIERS", "CHANNEL_LOAD_WEIGHTS",
    "BATTERY_MULTIPLIER", "Evidence", "DimensionScore", "RoadmapItem",
    "Profile", "Report", "composite_score", "confidence_from_tiers",
    "validate_dimension_scores", "compute_energy_budget",
    "engagement_load_hours", "budget_respected", "prioritize_roadmap",
    "detect_high_stimulation_stacking", "network_growth_score",
    "validate_gate", "devil_advocate_check", "assemble_report_section",
    "build_report",
]