#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_harness.py - runnable test suite for networking-coach-introverts.

Uses the Python standard-library `unittest` framework so it runs out of the
box with no third-party dependencies:

    python -m unittest discover -s tests -v
    # or directly:
    python tests/test_harness.py

These tests validate the deterministic engine and harness wiring, the
validation gate, scoring math, roadmap prioritization, devil's-advocate
enforcement, authenticity filters, tier caps, and degraded-mode behavior.
No model, network, or external API is invoked.
"""
import contextlib
import io
import os
import sys
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import harness  # noqa: E402
from scoring_engine import (  # noqa: E402
    DIMENSIONS, WEIGHTS, Evidence, DimensionScore, RoadmapItem, Profile,
    composite_score, confidence_from_tiers, validate_dimension_scores,
    compute_energy_budget, engagement_load_hours, budget_respected,
    prioritize_roadmap, detect_high_stimulation_stacking, network_growth_score,
    validate_gate, devil_advocate_check, build_report,
)


def _valid_dimension_scores(ng_score=68):
    """A fully-evidenced set of six dimension scores that passes all gates."""
    return [
        DimensionScore("goal_clarity", 72, "specific 3-wk metric [#fw-putnam-2000]",
                       [Evidence("#fw-putnam-2000", 3)]),
        DimensionScore("energy_sustainability", 78, "daily cap + recovery [#fw-cain-2012]",
                       [Evidence("#fw-cain-2012", 3)]),
        DimensionScore("authenticity_fit", 85, "give-first plain tone [#fw-grant-2013]",
                       [Evidence("#fw-grant-2013", 4), Evidence("#fw-cain-2012", 3)]),
        DimensionScore("conversation_readiness", 82, "opener+exit+qbank [#fw-giles-1991]",
                       [Evidence("#fw-giles-1991", 3)]),
        DimensionScore("follow_up_consistency", 70, "give-heavy cadence [#fw-grant-2013]",
                       [Evidence("#fw-grant-2013", 4)]),
        DimensionScore("network_growth", ng_score, "bridging pipeline [#fw-granovetter-1973]",
                       [Evidence("#fw-granovetter-1973", 2)]),
    ]


def _good_intake_raw(degraded=False):
    return {
        "goal": {"statement": "Make conference connections without burning out",
                 "type": "learning", "success_metric": "5 1:1 + 2 follow-ups",
                 "timeframe_weeks": 3, "priority": "primary"},
        "energy": {"social_battery": "low", "days_per_week_available": 3,
                   "hours_per_session_max": 2},
        "comfort_zones": {"preferred_channels": ["in_person_1on1", "async_text"],
                          "avoided_channels": ["large_event"]},
        "target_context": {"setting": "conference", "audience": "peers and seniors"},
        "meta": {"degraded_mode": degraded, "assumptions": []},
    }


def _good_scripts(context="conference", channel="in_person_1on1",
                  checks=None):
    checks = checks or {"no_transactional_opener": True, "specific_reference": True,
                        "history_aware": "n/a", "energy_aware_exit": True,
                        "tone_clean": True}
    return [{
        "context": context, "channel": channel,
        "opener": "Hi, what did you make of the talk?",
        "transition": "Reminded me of a write-up - want it?",
        "exit": "Grabbing a quiet coffee - can I message you?",
        "authenticity_checks": checks,
    }]


def _good_followup(score=74.0, a_members=None):
    return {
        "follow_up_consistency_score": score,
        "tiers": {"A": {"cap": 12, "members": a_members or []},
                  "B": {"cadence": "1 / 6-8 wks", "members": []},
                  "C": {"cadence": "outreach then evaluate", "members": []}},
        "crm_seed": [],
        "weekly_template": {"give_first_block": "share one resource",
                            "touches": [{"tier": "B", "type": "share_update", "count_per_week": 2}]},
        "reengagement_script": "Hi - been a while; sending this in case useful.",
        "rationale": "give-heavy weak-tie cadence [#fw-grant-2013][#fw-granovetter-1973]",
        "assumptions": [],
    }


def _good_roadmap_items():
    return [
        RoadmapItem("W1-1", 1, "Send 2 give-first async touches", "async_text", "B",
                    3, 1, "low", "M1", "early give-first win [#fw-grant-2013]"),
        RoadmapItem("W1-2", 1, "Prepare a give asset", "async_text", "self",
                    4, 2, "low", None, "asset before cold outreach [#fw-grant-2013]"),
        RoadmapItem("W2-1", 2, "Conference 1:1 within 2h/day cap", "in_person_1on1",
                    "C", 5, 3, "high", "M4", "depth over breadth [#fw-cain-2012]"),
        RoadmapItem("W3-1", 3, "Send 2 async follow-ups", "async_text", "C",
                    4, 1, "low", None, "weak-tie activation [#fw-granovetter-1973]"),
    ]


def _good_da():
    return {dim: "addressed: tested; score held" for dim in DIMENSIONS}


# ---------------------------------------------------------------------------
# Scoring engine tests
# ---------------------------------------------------------------------------

class ScoringEngineTests(unittest.TestCase):

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(WEIGHTS.values()), 1.0, places=6)

    def test_six_dimensions_present(self):
        self.assertEqual(len(DIMENSIONS), 6)
        self.assertEqual(set(DIMENSIONS), set(WEIGHTS))

    def test_composite_in_range_and_weighted(self):
        scores = _valid_dimension_scores()
        comp = composite_score(scores)
        self.assertGreater(comp, 0)
        self.assertLessEqual(comp, 100)
        expected = round(sum(WEIGHTS[s.dimension] * s.score for s in scores), 2)
        self.assertAlmostEqual(comp, expected, places=2)

    def test_composite_rejects_missing_dimension(self):
        scores = _valid_dimension_scores()[:-1]
        with self.assertRaises(ValueError):
            composite_score(scores)

    def test_dimension_score_range_enforced(self):
        with self.assertRaises(ValueError):
            DimensionScore("goal_clarity", 150, "x", [Evidence("#fw-putnam-2000", 3)])

    def test_dimension_score_requires_evidence(self):
        with self.assertRaises(ValueError):
            DimensionScore("goal_clarity", 70, "x", [])

    def _peer_share(self, scores):
        peer = sum(1 for s in scores
                   if any(e.tier <= 3 and not e.is_assumption for e in s.evidence))
        return peer / len(scores)

    def test_confidence_peer_reviewed_and_not_degraded(self):
        scores = _valid_dimension_scores()
        conf = confidence_from_tiers(scores, degraded_mode=False)
        expected = 0.4 * self._peer_share(scores) + 0.6 * 1.0
        self.assertAlmostEqual(conf, round(expected, 3), places=3)

    def test_confidence_degraded_mode_penalty(self):
        scores = _valid_dimension_scores()
        conf = confidence_from_tiers(scores, degraded_mode=True)
        expected = 0.4 * self._peer_share(scores) + 0.6 * 0.75
        self.assertAlmostEqual(conf, round(expected, 3), places=3)

    def test_validate_dimension_scores_passes_good(self):
        self.assertEqual(validate_dimension_scores(_valid_dimension_scores()), [])

    def test_validate_dimension_scores_flags_bad_tier(self):
        scores = _valid_dimension_scores()
        scores[0] = DimensionScore("goal_clarity", 70, "x",
                                   [Evidence("#fw-putnam-2000", 9)])
        errs = validate_dimension_scores(scores)
        self.assertTrue(any("tier" in e for e in errs))


# ---------------------------------------------------------------------------
# Energy budget tests
# ---------------------------------------------------------------------------

class EnergyBudgetTests(unittest.TestCase):

    def test_low_battery_budget(self):
        p = Profile("learning", "low", 3, 2, ["async_text"], [], 3)
        b = compute_energy_budget(p)
        # 3*2*0.35 = 2.1
        self.assertAlmostEqual(b["weekly_budget_session_hours"], 2.1, places=2)
        self.assertGreaterEqual(b["recovery_reserved_hours"], 0.42)

    def test_budget_respected(self):
        p = Profile("learning", "high", 5, 2, ["async_text"], [], 6)
        b = compute_energy_budget(p)
        self.assertTrue(budget_respected(b, {"async_text": 1.0}))

    def test_budget_exceeded_detected(self):
        p = Profile("learning", "low", 1, 1, ["large_event"], [], 2)
        b = compute_energy_budget(p)
        # low battery + large_event load 2.0 -> easily exceeded
        self.assertFalse(budget_respected(b, {"large_event": 5.0}))

    def test_unknown_channel_raises(self):
        with self.assertRaises(ValueError):
            engagement_load_hours({"telegram_dm": 1.0})


# ---------------------------------------------------------------------------
# Roadmap tests
# ---------------------------------------------------------------------------

class RoadmapTests(unittest.TestCase):

    def test_prioritize_sorts_by_priority_desc(self):
        items = _good_roadmap_items()
        ordered = prioritize_roadmap(items)
        priorities = [it.priority for it in ordered]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_high_stimulation_stacking_detected(self):
        items = [
            RoadmapItem("a", 1, "x", "large_event", "C", 5, 2, "high"),
            RoadmapItem("b", 1, "y", "small_group", "C", 4, 2, "high"),
            RoadmapItem("c", 2, "z", "async_text", "B", 3, 1, "low"),
        ]
        self.assertEqual(detect_high_stimulation_stacking(items), [1])

    def test_no_stacking_returns_empty(self):
        items = _good_roadmap_items()
        self.assertEqual(detect_high_stimulation_stacking(items), [])

    def test_roadmap_item_validates_impact_effort(self):
        with self.assertRaises(ValueError):
            RoadmapItem("x", 1, "y", "async_text", "B", 6, 1)
        with self.assertRaises(ValueError):
            RoadmapItem("x", 1, "y", "async_text", "B", 3, 0)

    def test_network_growth_score_bounds(self):
        self.assertEqual(network_growth_score(0, 0, 0), 0.0)
        self.assertEqual(network_growth_score(1, 1, 1), 100.0)
        with self.assertRaises(ValueError):
            network_growth_score(1.5, 0, 0)


# ---------------------------------------------------------------------------
# Gate tests
# ---------------------------------------------------------------------------

class GateTests(unittest.TestCase):

    def test_good_profile_passes_gate(self):
        p = Profile("learning", "low", 3, 2, ["async_text"], [], 3)
        self.assertEqual(validate_gate(p), [])

    def test_contradictory_channels_flagged(self):
        p = Profile("learning", "low", 3, 2, ["async_text", "phone"],
                    ["async_text", "phone"], 3)
        errs = validate_gate(p)
        self.assertTrue(any("contradictory" in e for e in errs))

    def test_zero_timeframe_flagged(self):
        p = Profile("learning", "low", 3, 2, ["async_text"], [], 0)
        self.assertTrue(any("timeframe" in e for e in validate_gate(p)))

    def test_empty_channels_flagged(self):
        p = Profile("learning", "low", 3, 2, [], [], 3)
        self.assertTrue(any("preferred_channels" in e for e in validate_gate(p)))


# ---------------------------------------------------------------------------
# Devil's advocate tests
# ---------------------------------------------------------------------------

class DevilsAdvocateTests(unittest.TestCase):

    def test_all_addressed_passes(self):
        da = _good_da()
        self.assertEqual(devil_advocate_check(da, DIMENSIONS), [])

    def test_missing_dimension_flagged(self):
        da = _good_da()
        da["energy_sustainability"] = ""
        missing = devil_advocate_check(da, DIMENSIONS)
        self.assertIn("energy_sustainability", missing)


# ---------------------------------------------------------------------------
# Harness pipeline tests (the five core scenarios + edges)
# ---------------------------------------------------------------------------

class PipelineTests(unittest.TestCase):

    def _run_good(self, **overrides):
        kw = dict(
            intake_raw=_good_intake_raw(),
            scripts=_good_scripts(),
            question_bank=["What surprised you most?"],
            dimension_scores=_valid_dimension_scores(),
            followup=_good_followup(),
            roadmap_items=_good_roadmap_items(),
            milestones=[{"id": "M1", "trigger": "give-first sent", "status": "pending"}],
            ng_components=(0.7, 0.6, 0.75),
            devils_advocate=_good_da(),
        )
        kw.update(overrides)
        return harness.run_pipeline(**kw)

    def test_happy_path_ok(self):
        res = self._run_good()
        self.assertTrue(res.ok, msg=str(res.errors))
        self.assertEqual(res.exit_code, 0)
        self.assertIsNotNone(res.report)
        self.assertGreater(res.report.composite, 0)

    def test_intake_holds_for_missing_fields(self):
        raw = _good_intake_raw()
        del raw["goal"]["success_metric"]
        res = self._run_good(intake_raw=raw)
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 2)
        self.assertTrue(res.clarifying_questions)

    def test_gate_blocks_contradictory_channels(self):
        raw = _good_intake_raw()
        raw["comfort_zones"]["avoided_channels"] = list(raw["comfort_zones"]["preferred_channels"])
        res = self._run_good(intake_raw=raw)
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 2)

    def test_filter_failure_blocks_output(self):
        bad_scripts = _good_scripts(checks={
            "no_transactional_opener": False, "specific_reference": True,
            "history_aware": "n/a", "energy_aware_exit": True, "tone_clean": True})
        res = self._run_good(scripts=bad_scripts)
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 3)
        self.assertTrue(any("transactional" in e for e in res.errors))

    def test_missing_devils_advocate_blocks_output(self):
        res = self._run_good(devils_advocate={})
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 3)
        self.assertTrue(any("devil" in e for e in res.errors))

    def test_missing_dimension_blocks_output(self):
        # A dimension dropped entirely must be caught by the scoring validator.
        scores = _valid_dimension_scores()[:-1]
        res = self._run_good(dimension_scores=scores)
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 3)

    def test_tier_a_cap_enforced(self):
        fu = _good_followup(a_members=[{"name": "c%d" % i} for i in range(13)])
        res = self._run_good(followup=fu)
        self.assertFalse(res.ok)
        self.assertEqual(res.exit_code, 3)
        self.assertTrue(any("Tier A" in e for e in res.errors))

    def test_degraded_mode_lowers_confidence(self):
        res_on = self._run_good(intake_raw=_good_intake_raw(degraded=False))
        res_off = self._run_good(intake_raw=_good_intake_raw(degraded=True))
        self.assertTrue(res_on.ok and res_off.ok)
        self.assertLess(res_off.report.confidence, res_on.report.confidence)
        self.assertTrue(res_off.report.degraded_mode)

    def test_network_growth_overrides_llm_score_with_computed(self):
        res = self._run_good(dimension_scores=_valid_dimension_scores(ng_score=10),
                             ng_components=(1.0, 1.0, 1.0))
        self.assertTrue(res.ok)
        ng = next(s for s in res.report.dimension_scores if s.dimension == "network_growth")
        self.assertAlmostEqual(ng.score, 100.0, places=2)

    def test_roadmap_is_prioritized_in_report(self):
        res = self._run_good()
        priorities = [it.priority for it in res.report.roadmap]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_demo_runs_clean(self):
        # exercises the built-in end-to-end example used in CI smoke tests
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = harness._demo()
        self.assertEqual(rc, 0)
        self.assertIn("Composite score", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)