"""
benchmark/pure_strips_benchmarks.py
Curated Pure STRIPS + Typing Benchmark Loaders for AutoPlanBench & NL2PDDL.

Strictly filters for domains that ONLY contain (:requirements :strips :typing)
or a subset thereof (no :equality, :negative-preconditions, :disjunctive-preconditions,
:adl, :action-costs, :fluents, etc.).

Reads directly from original repository folders:
  - AutoPlanBench: autoplanbench/data/<domain>/
  - NL2PDDL: NL2PDDL/test/<domain>/
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from config.paths import get_autoplanbench_dir, get_nl2pddl_dir

# ==============================================================================
# Filtered Top-10 Pure STRIPS + Typing Benchmark Domains
# ==============================================================================

AUTOPLANBENCH_PURE_STRIPS_10 = [
    "gripper",
    "depot",
    "satellite",
    "rovers",
    "barman14-bfs",
    "blocksworld",
    "logistics",
    "elevators08",
    "floortile",
    "parking11"
]

NL2PDDL_PURE_STRIPS_10 = [
    "CLEANING",
    "DOCK_WORKER",
    "GRID",
    "GRIPPER",
    "HANOI",
    "HIKING",
    "MINING",
    "SATELLITE",
    "SOKOBAN",
    "SPANNER"
]

NL2PDDL_NARRATIVES = {
    "CLEANING": "The Cleaning domain involves cleaning robots navigating rooms, picking up debris, and using cleaning tools to sterilize surfaces.",
    "DOCK_WORKER": "The Dock Worker domain involves cranes loading and unloading shipping containers from trucks and stacking them onto pallets in dock depots.",
    "GRID": "The Grid domain involves a robot moving across an interconnected grid of locations. The robot can pick up keys of various shapes, use keys to unlock matching doors between cells, and carry objects.",
    "GRIPPER": "The Gripper domain involves a robot with two mechanical grippers (left and right) moving between rooms to transport balls from their source rooms to designated target rooms.",
    "HANOI": "The Towers of Hanoi domain involves moving discs between pegs. A disc can only be placed on a larger disc or an empty peg, and only the topmost disc of a peg can be moved at any time.",
    "HIKING": "The Hiking domain involves a group of hikers walking along trails between designated locations. Hikers must walk in pairs and set up tents to rest at waypoints before continuing their journey.",
    "MINING": "The Mining domain involves extracting mineral deposits using mining equipment, loading ore into haulers, and transporting raw ore to processing plants.",
    "SATELLITE": "The Satellite domain involves satellites equipped with observation instruments orbiting to take images of celestial targets. Satellites can turn between directions. Instruments must be on board, powered on, and calibrated pointing at an orientation before taking an image in a supported mode.",
    "SOKOBAN": "The Sokoban domain involves a warehouse robot pushing boxes across adjacent grid locations to target destination squares. The robot cannot pull boxes, and spaces must be clear to navigate or push.",
    "SPANNER": "The Spanner domain involves a mobile agent traversing a one-way path of locations from a shed to a gate to collect spanners and tighten loose nuts at the gate. Each spanner can be used only once."
}


# ==============================================================================
# AutoPlanBench Original Loader
# ==============================================================================

def get_autoplanbench_domain_folder(domain_name: str) -> Path:
    return Path(get_autoplanbench_dir()) / domain_name


def list_autoplanbench_problem_files(domain_name: str) -> List[str]:
    """Lists sorted problem PDDL files from autoplanbench/data/<domain>/orig_problems/."""
    probs_dir = get_autoplanbench_domain_folder(domain_name) / "orig_problems"
    if not probs_dir.exists():
        return []
    def _extract_num(name: str) -> int:
        m = re.search(r'\d+', name)
        return int(m.group(0)) if m else 9999
    return sorted([f for f in os.listdir(probs_dir) if f.endswith(".pddl")], key=_extract_num)


def translate_autoplanbench_problem(prob_pddl: str, pred_maps: Dict[str, str], instance_name: str, domain_name: str) -> str:
    """Translates objects, init, and goal facts from problem PDDL into structured readable text."""
    obj_match = re.search(r'\(:objects\s*(.*?)\)', prob_pddl, re.IGNORECASE | re.DOTALL)
    objects_nl = []
    if obj_match:
        raw_objs = obj_match.group(1).strip()
        for line in raw_objs.split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                objects_nl.append(line)

    init_match = re.search(r'\(:init\s*(.*?)\(:goal', prob_pddl, re.IGNORECASE | re.DOTALL)
    init_facts = []
    if init_match:
        for fact in re.findall(r'\(([^()]+)\)', init_match.group(1)):
            parts = fact.strip().split()
            if not parts:
                continue
            pname, args = parts[0], parts[1:]
            if pname == '=':
                continue
            if pname in pred_maps:
                try:
                    init_facts.append(pred_maps[pname].format(*args))
                except Exception:
                    init_facts.append(f"{pname} ({', '.join(args)})")
            elif pname.lower() in pred_maps:
                try:
                    init_facts.append(pred_maps[pname.lower()].format(*args))
                except Exception:
                    init_facts.append(f"{pname} ({', '.join(args)})")
            else:
                init_facts.append(f"{pname} ({', '.join(args)})")

    goal_match = re.search(r'\(:goal\s*(.*)', prob_pddl, re.IGNORECASE | re.DOTALL)
    goal_facts = []
    if goal_match:
        for fact in re.findall(r'\(([^()]+)\)', goal_match.group(1)):
            parts = fact.strip().split()
            if not parts or parts[0].lower() in ('and', 'or', 'not'):
                continue
            pname, args = parts[0], parts[1:]
            if pname in pred_maps:
                try:
                    goal_facts.append(pred_maps[pname].format(*args))
                except Exception:
                    goal_facts.append(f"{pname} ({', '.join(args)})")
            elif pname.lower() in pred_maps:
                try:
                    goal_facts.append(pred_maps[pname.lower()].format(*args))
                except Exception:
                    goal_facts.append(f"{pname} ({', '.join(args)})")
            else:
                goal_facts.append(f"{pname} ({', '.join(args)})")

    lines = [f"Problem Instance: {instance_name} (Domain: {domain_name})"]
    if objects_nl:
        lines.append("\nObjects:")
        for obj in objects_nl:
            lines.append(f"- {obj}")
    if init_facts:
        lines.append("\nInitial State:")
        for f in init_facts:
            lines.append(f"- {f}")
    if goal_facts:
        lines.append("\nGoal State:")
        for f in goal_facts:
            lines.append(f"- {f}")

    return "\n".join(lines)


def load_autoplanbench_original_domain_data(
    domain_name: str,
    selected_instance: Optional[str] = None
) -> Tuple[str, str, str, str, str, List[str]]:
    """
    Loads requirements, ground-truth domain PDDL, and problem instance directly
    from autoplanbench/data/<domain_name>/.
    
    Returns:
      (unified_prompt, domain_desc, problem_desc, ref_domain_pddl, ref_problem_pddl, problem_files)
    """
    d_dir = get_autoplanbench_domain_folder(domain_name)
    
    # 1. Domain description
    dom_desc = ""
    enc_path = d_dir / "domain_encoding.txt"
    if enc_path.exists():
        with open(enc_path, "r", encoding="utf-8", errors="ignore") as f:
            dom_desc = f.read().strip()
    else:
        seed1_path = d_dir / "domain_description_seed1.json"
        if seed1_path.exists():
            with open(seed1_path, "r", encoding="utf-8", errors="ignore") as f:
                sdata = json.load(f)
                dom_desc = sdata.get("domain_intro", f"Natural language specification for {domain_name}")

    # 2. Reference ground-truth domain PDDL
    ref_dom = ""
    dom_pddl_path = d_dir / "domain.pddl"
    if dom_pddl_path.exists():
        with open(dom_pddl_path, "r", encoding="utf-8", errors="ignore") as f:
            ref_dom = f.read()

    # 3. Predicate mappings for problem translation
    pred_maps = {}
    seed1_path = d_dir / "domain_description_seed1.json"
    if seed1_path.exists():
        try:
            with open(seed1_path, "r", encoding="utf-8", errors="ignore") as f:
                sdata = json.load(f)
                pred_maps = sdata.get("predicate_mappings", {})
        except Exception:
            pred_maps = {}

    # 4. Problem files & selected instance
    prob_files = list_autoplanbench_problem_files(domain_name)
    inst_name = selected_instance if selected_instance and selected_instance in prob_files else (prob_files[0] if prob_files else "instance-1.pddl")
    
    ref_inst = ""
    prob_desc = ""
    inst_path = d_dir / "orig_problems" / inst_name
    if inst_path.exists():
        with open(inst_path, "r", encoding="utf-8", errors="ignore") as f:
            ref_inst = f.read()
        prob_desc = translate_autoplanbench_problem(ref_inst, pred_maps, inst_name, domain_name)

    unified_prompt = f"{dom_desc}\n\n{prob_desc}".strip()
    return unified_prompt, dom_desc, prob_desc, ref_dom, ref_inst, prob_files


# ==============================================================================
# NL2PDDL Original Loader
# ==============================================================================

def get_nl2pddl_domain_folder(domain_name: str) -> Path:
    return Path(get_nl2pddl_dir()) / domain_name


def list_nl2pddl_problem_files(domain_name: str) -> List[str]:
    """Lists problem PDDL files from NL2PDDL/test/<domain>/problems/."""
    probs_dir = get_nl2pddl_domain_folder(domain_name) / "problems"
    if not probs_dir.exists():
        return []
    files = [
        f for f in os.listdir(probs_dir)
        if f.endswith(".pddl") and (probs_dir / f).stat().st_size > 0
    ]
    if "problem_gold.pddl" in files:
        files.remove("problem_gold.pddl")
        files.insert(0, "problem_gold.pddl")
    return files


def generate_nl2pddl_domain_text(domain_pddl: str, domain_name: str) -> str:
    """Generates structured natural language specification from gold domain PDDL."""
    narrative = NL2PDDL_NARRATIVES.get(domain_name.upper(), f"The {domain_name} planning domain.")
    
    types_match = re.search(r'\(:types\s+(.*?)\)', domain_pddl, re.IGNORECASE | re.DOTALL)
    types_lines = []
    if types_match:
        for line in types_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                types_lines.append(line)

    actions = []
    for act in re.finditer(r'\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*\Z)', domain_pddl, re.IGNORECASE | re.DOTALL):
        act_name = act.group(1)
        body = act.group(2)
        params_match = re.search(r':parameters\s*\((.*?)\)', body, re.IGNORECASE | re.DOTALL)
        params_str = params_match.group(1).strip() if params_match else ""
        actions.append((act_name, params_str))

    lines = [
        f"Domain Overview:\n{narrative.strip()}\n",
        f"Domain Name: {domain_name}"
    ]
    if types_lines:
        lines.append("\nEntity Types Hierarchy:")
        for tl in types_lines:
            lines.append(f"  - {tl}")
    if actions:
        lines.append("\nSupported Actions:")
        for aname, aparams in actions:
            clean_params = re.sub(r'\s+', ' ', aparams).strip()
            lines.append(f"  - {aname} ({clean_params})")

    return "\n".join(lines)


def generate_nl2pddl_problem_text(prob_pddl: str, prob_name: str, domain_name: str) -> str:
    """Generates natural language problem scenario from gold problem PDDL."""
    obj_match = re.search(r'\(:objects\s*(.*?)\)', prob_pddl, re.IGNORECASE | re.DOTALL)
    objects_lines = []
    if obj_match:
        for line in obj_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                objects_lines.append(line)

    init_match = re.search(r'\(:init\s*(.*?)\(:goal', prob_pddl, re.IGNORECASE | re.DOTALL)
    init_facts = []
    if init_match:
        for fact in re.findall(r'\(([^()]+)\)', init_match.group(1)):
            fact = fact.strip()
            if fact and not fact.startswith('='):
                init_facts.append(fact)

    goal_match = re.search(r'\(:goal\s*(.*)', prob_pddl, re.IGNORECASE | re.DOTALL)
    goal_facts = []
    if goal_match:
        for fact in re.findall(r'\(([^()]+)\)', goal_match.group(1)):
            fact = fact.strip()
            if fact and not fact.startswith('='):
                parts = fact.split()
                if parts and parts[0].lower() not in ('and', 'or', 'not'):
                    goal_facts.append(fact)

    lines = [f"Problem Scenario: {prob_name} (Domain: {domain_name})"]
    if objects_lines:
        lines.append("\nObjects:")
        for ol in objects_lines:
            lines.append(f"  - {ol}")
    if init_facts:
        lines.append("\nInitial State Facts:")
        for ifact in init_facts:
            lines.append(f"  - ({ifact})")
    if goal_facts:
        lines.append("\nGoal Objectives:")
        for gfact in goal_facts:
            lines.append(f"  - ({gfact})")

    return "\n".join(lines)


def load_nl2pddl_original_domain_data(
    domain_name: str,
    selected_instance: Optional[str] = None
) -> Tuple[str, str, str, str, str, List[str]]:
    """
    Loads requirements, ground-truth domain PDDL, and problem instance directly
    from NL2PDDL/test/<domain_name>/.
    
    Returns:
      (unified_prompt, domain_desc, problem_desc, ref_domain_pddl, ref_problem_pddl, problem_files)
    """
    d_dir = get_nl2pddl_domain_folder(domain_name)
    doms_dir = d_dir / "domains"
    probs_dir = d_dir / "problems"
    
    ref_dom = ""
    dom_desc = ""
    if doms_dir.exists():
        dom_files = [f for f in os.listdir(doms_dir) if f.endswith(".pddl")]
        gold_d = "domain_gold.pddl" if "domain_gold.pddl" in dom_files else (dom_files[0] if dom_files else None)
        if gold_d:
            with open(doms_dir / gold_d, "r", encoding="utf-8", errors="ignore") as f:
                ref_dom = f.read()
            dom_desc = generate_nl2pddl_domain_text(ref_dom, domain_name)

    prob_files = list_nl2pddl_problem_files(domain_name)
    inst_name = selected_instance if selected_instance and selected_instance in prob_files else (prob_files[0] if prob_files else "problem_gold.pddl")

    ref_inst = ""
    prob_desc = ""
    if probs_dir.exists() and (probs_dir / inst_name).exists():
        with open(probs_dir / inst_name, "r", encoding="utf-8", errors="ignore") as f:
            ref_inst = f.read()
        prob_desc = generate_nl2pddl_problem_text(ref_inst, inst_name, domain_name)

    unified_prompt = f"=== DOMAIN SPECIFICATION ===\n{dom_desc}\n\n=== PROBLEM SCENARIO ===\n{prob_desc}".strip()
    return unified_prompt, dom_desc, prob_desc, ref_dom, ref_inst, prob_files
