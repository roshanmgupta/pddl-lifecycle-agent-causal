#!/usr/bin/env python3
"""
tests/test_causal_graph_triage.py
Empirical validation suite for classical Causal Graph & DTG Invariant Fault Localization.
Tests 3 benchmark domains:
1. Gripper: DTG Irreversible / Absorbing State Trap (Missing reverse action).
2. Blocksworld: Circular Precondition Deadlock Cycle.
3. Satellite: Mutex Self-Contradiction & Non-Goal Leaf Bloat Action.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.sbfl_analyzer import run_causal_graph_sbfl_analysis
from nodes.triage import parse_fast_downward_log

def test_gripper_absorbing_state():
    print("=" * 70)
    print("TEST 1: Gripper Domain — DTG Irreversible / Absorbing State Trap")
    print("Scenario: 'drop' action is missing, so 'pick' deletes 'free' irreversibly.")
    print("=" * 70)

    # Gripper domain with missing 'drop' action
    domain_bp = {
        "domain_name": "gripper-strips",
        "actions": [
            {
                "action_name": "move",
                "parameters": {"?r": "robot", "?from": "room", "?to": "room"},
                "preconditions": ["(at-robby ?r ?from)"],
                "effects": ["(at-robby ?r ?to)", "(not (at-robby ?r ?from))"]
            },
            {
                "action_name": "pick",
                "parameters": {"?r": "robot", "?obj": "object", "?room": "room", "?g": "gripper"},
                "preconditions": ["(at ?obj ?room)", "(at-robby ?r ?room)", "(free ?r ?g)"],
                "effects": ["(carry ?r ?obj ?g)", "(not (at ?obj ?room))", "(not (free ?r ?g))"]
            }
            # 'drop' action is completely omitted!
        ]
    }

    problem_bp = {
        "init": ["(at-robby r1 rooma)", "(free r1 left)", "(at ball1 rooma)"],
        "goal": ["(at ball1 roomb)"]
    }

    raw_errors = ["Planner Error: completely explored state space -- no solution"]

    res = run_causal_graph_sbfl_analysis(domain_bp, problem_bp, raw_errors)
    reports = parse_fast_downward_log("completely explored state space -- no solution", causal_analysis=res)

    print("\n[Causal Graph Summary]:")
    print(res["diagnostic_summary"])

    print("\n[Generated Triage Diagnostic Reports]:")
    for idx, r in enumerate(reports, 1):
        print(f" {idx}. [{r.error_category.value}] Element: {r.faulty_element} | Score: {r.suspiciousness_score} | Op: {r.repair_operation_type.value}")
        print(f"    Hint: {r.suggested_repair_hint}")

    assert any(it["predicate"] == "free" for it in res["irreversible_transitions"]), "Failed to detect irreversible predicate 'free'!"
    assert res["top_action"] == "pick", f"Expected top action 'pick', got {res['top_action']}"
    print("\n>>> TEST 1 PASSED: Successfully detected DTG absorbing state lockout on 'free'!\n")

def test_blocksworld_deadlock_cycle():
    print("=" * 70)
    print("TEST 2: Blocksworld Domain — Circular Precondition Deadlock Cycle")
    print("Scenario: 'pick-up' mistakenly requires 'holding' instead of 'handempty',")
    print("creating a mutual dependency loop where 'pick-up' requires what it asserts.")
    print("=" * 70)

    domain_bp = {
        "domain_name": "blocksworld",
        "actions": [
            {
                "action_name": "pick-up",
                "parameters": {"?x": "block"},
                "preconditions": ["(clear ?x)", "(holding ?x)"], # Fault: Requires holding!
                "effects": ["(holding ?x)", "(not (clear ?x))", "(not (handempty))"]
            },
            {
                "action_name": "put-down",
                "parameters": {"?x": "block"},
                "preconditions": ["(holding ?x)"],
                "effects": ["(clear ?x)", "(handempty)", "(on-table ?x)", "(not (holding ?x))"]
            }
        ]
    }

    problem_bp = {
        "init": ["(clear b1)", "(handempty)", "(on-table b1)"],
        "goal": ["(holding b1)"]
    }

    raw_errors = ["Planner Error: search stopped without finding a solution (deadlock)"]

    res = run_causal_graph_sbfl_analysis(domain_bp, problem_bp, raw_errors)
    reports = parse_fast_downward_log("search stopped without finding a solution", causal_analysis=res)

    print("\n[Causal Graph Summary]:")
    print(res["diagnostic_summary"])

    print("\n[Generated Triage Diagnostic Reports]:")
    for idx, r in enumerate(reports, 1):
        print(f" {idx}. [{r.error_category.value}] Element: {r.faulty_element} | Score: {r.suspiciousness_score} | Op: {r.repair_operation_type.value}")
        print(f"    Hint: {r.suggested_repair_hint}")

    assert len(res["causal_cycles"]) > 0, "Failed to detect causal cycle!"
    print("\n>>> TEST 2 PASSED: Successfully detected circular causal deadlock loop!\n")

def test_satellite_mutex_and_leaf_bloat():
    print("=" * 70)
    print("TEST 3: Satellite Domain — Mutex Contradiction & Non-Goal Leaf Bloat")
    print("Scenario: 'calibrate' action simultaneously adds and deletes 'calibrated',")
    print("and an extra hallucinated 'refuel' action produces an unused predicate.")
    print("=" * 70)

    domain_bp = {
        "domain_name": "satellite",
        "actions": [
            {
                "action_name": "turn_to",
                "parameters": {"?s": "satellite", "?d_new": "direction", "?d_prev": "direction"},
                "preconditions": ["(pointing ?s ?d_prev)"],
                "effects": ["(pointing ?s ?d_new)", "(not (pointing ?s ?d_prev))"]
            },
            {
                "action_name": "calibrate",
                "parameters": {"?s": "satellite", "?i": "instrument", "?d": "direction"},
                "preconditions": ["(on_board ?i ?s)", "(pointing ?s ?d)"],
                # Fault: Simultaneously asserts and negates calibrated!
                "effects": ["(calibrated ?i)", "(not (calibrated ?i))"]
            },
            {
                "action_name": "take_image",
                "parameters": {"?s": "satellite", "?d": "direction", "?i": "instrument", "?m": "mode"},
                "preconditions": ["(calibrated ?i)", "(pointing ?s ?d)"],
                "effects": ["(have_image ?d ?m)"]
            },
            {
                # Non-goal leaf / bloat action
                "action_name": "refuel_thrusters",
                "parameters": {"?s": "satellite"},
                "preconditions": ["(on_board ?s)"],
                "effects": ["(fuel_full ?s)"]
            }
        ]
    }

    problem_bp = {
        "init": ["(pointing sat1 dir_calib)", "(on_board inst1 sat1)"],
        "goal": ["(have_image dir_target mode_spec)"]
    }

    raw_errors = ["VAL Error: contradictory effects in action calibrate"]

    res = run_causal_graph_sbfl_analysis(domain_bp, problem_bp, raw_errors)

    print("\n[Causal Graph Summary]:")
    print(res["diagnostic_summary"])

    assert len(res["internal_contradictions"]) > 0, "Failed to detect internal contradiction!"
    assert "refuel_thrusters" in res["non_goal_leaf_actions"], "Failed to detect non-goal leaf action 'refuel_thrusters'!"
    assert res["top_action"] == "calibrate", f"Expected top action 'calibrate', got {res['top_action']}"
    assert res["top_score"] == 1.00, f"Expected top score 1.00, got {res['top_score']}"
    print("\n>>> TEST 3 PASSED: Successfully detected Mutex Contradiction (Score 1.0) and Non-Goal Leaf Bloat!\n")

if __name__ == "__main__":
    print("\nRUNNING EMPIRICAL CAUSAL GRAPH & DTG TRIAGE TEST SUITE...\n")
    test_gripper_absorbing_state()
    test_blocksworld_deadlock_cycle()
    test_satellite_mutex_and_leaf_bloat()
    print("=" * 70)
    print("ALL 3 DOMAIN CAUSAL GRAPH INVARIANT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)
