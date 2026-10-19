#!/usr/bin/env python3
"""
Extract Domain and Problem Natural Language Descriptions from AutoPlanBench.

Saves descriptions for all 77 domains into:
    prompt/<domain_name>/domain_description.txt
    prompt/<domain_name>/problem_description.txt
"""

import os
import json
import re
from pathlib import Path


def extract_number(filename: str) -> int:
    """Extract numeric instance index from filename for natural sorting."""
    match = re.search(r'\d+', filename)
    return int(match.group(0)) if match else 999999


def get_first_problem_file(probs_dir: str) -> tuple[str, str] | None:
    """Return (file_path, filename) for the lowest-indexed problem file."""
    if not os.path.isdir(probs_dir):
        return None
    files = [f for f in os.listdir(probs_dir) if f.endswith('.pddl')]
    if not files:
        return None
    files.sort(key=extract_number)
    return os.path.join(probs_dir, files[0]), files[0]


def extract_domain_description(data_dir: str, domain_name: str) -> str:
    """Extract the domain NL description."""
    enc_path = os.path.join(data_dir, "domain_encoding.txt")
    if os.path.exists(enc_path):
        with open(enc_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content

    # Fallback to seed1 JSON domain_intro
    desc_path = os.path.join(data_dir, "domain_description_seed1.json")
    if os.path.exists(desc_path):
        with open(desc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            intro = data.get("domain_intro", "").strip()
            if intro:
                return intro
            # If no domain_intro, synthesize from action descriptions
            actions = data.get("actions", {})
            if actions:
                lines = [f"Domain: {domain_name}", "\nAvailable Actions:"]
                for act_name, act_info in actions.items():
                    descr = act_info.get("description", act_name)
                    preconds = act_info.get("preconditions", [])
                    effects = act_info.get("effects", [])
                    lines.append(f"\nAction: {descr}")
                    if preconds:
                        lines.append("  Preconditions: " + "; ".join(preconds))
                    if effects:
                        lines.append("  Effects: " + "; ".join(effects))
                return "\n".join(lines)

    return f"Domain description not found for {domain_name}."


def parse_and_translate_problem(prob_pddl: str, pred_maps: dict, instance_name: str, domain_name: str) -> str:
    """Parse problem PDDL and translate objects, initial state, and goal into readable text."""
    # 1. Objects
    obj_match = re.search(r'\(:objects\s*(.*?)\)', prob_pddl, re.IGNORECASE | re.DOTALL)
    objects_nl = []
    if obj_match:
        raw_objs = obj_match.group(1).strip()
        if '-' in raw_objs:
            for line in raw_objs.split('\n'):
                line = line.strip()
                if line and '-' in line:
                    parts = line.split('-', 1)
                    objects_nl.append(f"{parts[0].strip()} - {parts[1].strip()}")
                elif line:
                    objects_nl.append(line)
        else:
            objs = raw_objs.split()
            if objs:
                objects_nl.append(" ".join(objs) + " - object")

    # 2. Initial state facts
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
            pname_lower = pname.lower()
            if pname in pred_maps:
                try:
                    init_facts.append(pred_maps[pname].format(*args))
                except Exception:
                    init_facts.append(f"{pname} ({', '.join(args)})")
            elif pname_lower in pred_maps:
                try:
                    init_facts.append(pred_maps[pname_lower].format(*args))
                except Exception:
                    init_facts.append(f"{pname} ({', '.join(args)})")
            else:
                init_facts.append(f"{pname} ({', '.join(args)})")

    # 3. Goal state facts
    goal_match = re.search(r'\(:goal\s*(.*)', prob_pddl, re.IGNORECASE | re.DOTALL)
    goal_facts = []
    if goal_match:
        for fact in re.findall(r'\(([^()]+)\)', goal_match.group(1)):
            parts = fact.strip().split()
            if not parts or parts[0].lower() in ('and', 'or', 'not'):
                continue
            pname, args = parts[0], parts[1:]
            pname_lower = pname.lower()
            if pname in pred_maps:
                try:
                    goal_facts.append(pred_maps[pname].format(*args))
                except Exception:
                    goal_facts.append(f"{pname} ({', '.join(args)})")
            elif pname_lower in pred_maps:
                try:
                    goal_facts.append(pred_maps[pname_lower].format(*args))
                except Exception:
                    goal_facts.append(f"{pname} ({', '.join(args)})")
            else:
                goal_facts.append(f"{pname} ({', '.join(args)})")

    # Format the problem description text
    lines = [
        f"Problem Instance: {instance_name} (Domain: {domain_name})",
        "",
        "Objects:",
    ]
    for obj in objects_nl:
        lines.append(f"- {obj}")

    lines.append("\nInitial State:")
    for fact in init_facts:
        lines.append(f"- {fact}")

    lines.append("\nGoal State:")
    for goal in goal_facts:
        lines.append(f"- {goal}")

    return "\n".join(lines)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "autoplanbench" / "data"
    output_base_dir = root_dir / "prompt_autoplanbench"

    if not data_dir.exists():
        print(f"Error: AutoPlanBench data directory not found at {data_dir}")
        return

    domains = sorted([d for d in os.listdir(data_dir) if (data_dir / d).is_dir()])
    print(f"Found {len(domains)} domains in {data_dir}")

    count = 0
    for domain in domains:
        domain_path = data_dir / domain
        domain_prompt_dir = output_base_dir / domain
        domain_prompt_dir.mkdir(parents=True, exist_ok=True)

        # 1. Extract domain description
        domain_desc = extract_domain_description(str(domain_path), domain)
        dom_out_file = domain_prompt_dir / "domain_description.txt"
        with open(dom_out_file, "w", encoding="utf-8") as f:
            f.write(domain_desc + "\n")

        # 2. Extract problem description
        desc_json_path = domain_path / "domain_description_seed1.json"
        pred_maps = {}
        if desc_json_path.exists():
            with open(desc_json_path, "r", encoding="utf-8") as f:
                desc_json = json.load(f)
                pred_maps = desc_json.get("predicate_mappings", {})

        probs_dir = str(domain_path / "orig_problems")
        prob_info = get_first_problem_file(probs_dir)
        if prob_info:
            prob_file_path, inst_name = prob_info
            with open(prob_file_path, "r", encoding="utf-8") as f:
                prob_pddl = f.read()
            prob_desc = parse_and_translate_problem(prob_pddl, pred_maps, inst_name, domain)
        else:
            prob_desc = f"No problem instance files found in {probs_dir}."

        prob_out_file = domain_prompt_dir / "problem_description.txt"
        with open(prob_out_file, "w", encoding="utf-8") as f:
            f.write(prob_desc + "\n")

        count += 1
        print(f"[{count:02d}/{len(domains)}] Extracted {domain} -> {domain_prompt_dir.relative_to(root_dir)}")

    print(f"\nCompleted! Extracted descriptions for all {count} domains into '{output_base_dir.relative_to(root_dir)}/'.")


if __name__ == "__main__":
    main()
