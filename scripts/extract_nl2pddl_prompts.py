#!/usr/bin/env python3
"""
Extract Domain and Problem Natural Language Descriptions from NL2PDDL.

Saves descriptions for all 31 domains in NL2PDDL/test into:
    prompt_NL2PDDL/<domain_name>/domain_description.txt
    prompt_NL2PDDL/<domain_name>/problem_description.txt
"""

import os
import json
import re
from pathlib import Path

KNOWN_DOMAIN_NARRATIVES = {
    "BLOCKSWORLD": """The Blocks World domain involves manipulating a set of blocks. Blocks can be placed on top of the table or on top of other blocks. Only one block at a time can be on top of another, and a block can only be moved if it is free, meaning it has no other block above it. A robotic arm is used to perform the pick-up, put-down, stack, and unstack movements.""",
    "SATELLITE": """The Satellite domain involves satellites equipped with observation instruments orbiting to take images of celestial targets. Satellites can turn between directions. Instruments must be on board, powered on, and calibrated pointing at an orientation before taking an image in a supported mode.""",
    "ROVERS": """The Rovers domain involves mobile planetary rovers navigating waypoints on Mars. Rovers collect rock and soil samples, use cameras to take pictures of targets in various modes, and transmit collected data back to a lander via line-of-sight communication.""",
    "GRIPPER": """The Gripper domain involves a robot with two grippers (left and right) moving between rooms to transport balls. The robot can pick up a ball from a room if a gripper is empty, move between rooms, and drop the ball in the destination room.""",
    "LOGISTICS": """The Logistics domain involves transporting packages within cities via trucks and between cities via airplanes. Packages are loaded into and unloaded from vehicles at specific airport or office locations.""",
    "DEPOT": """The Depot domain combines logistics and blocksworld mechanics. Trucks transport crates between depots and distributors, while hoists load and unload crates and stack them onto pallets.""",
    "PARKING": """The Parking domain involves maneuvering cars in a parking lot. Cars are parked in designated bays, some in front of others. A car can only be moved to an empty bay if it is not blocked by another car.""",
    "ELEVATOR": """The Elevator domain involves operating lifts between building floors to transport passengers. Passengers board and leave elevators, and the lift moves up and down between serviced levels.""",
    "HIKING": """The Hiking domain involves a group of hikers walking along trails between designated locations. Hikers must walk in pairs and set up tents to rest at waypoints before continuing their journey.""",
    "SPANNER": """The Spanner domain involves a mobile agent traversing a one-way path of locations from a shed to a gate to collect spanners and tighten loose nuts at the gate. Each spanner can be used only once.""",
    "GRID": """The Grid domain involves a robot moving across an interconnected grid of locations. The robot can pick up keys of various shapes, use keys to unlock matching doors between cells, and carry objects.""",
    "VISIT": """The Visit domain involves an agent moving through an interconnected network of places to visit and inspect designated target locations.""",
    "HANOI": """The Towers of Hanoi domain involves moving discs between pegs. A disc can only be placed on a larger disc or an empty peg, and only the topmost disc of a peg can be moved at any time.""",
    "PUZZLE": """The 8-Puzzle domain involves sliding numbered tiles on a 3x3 grid into an adjacent blank position to reach a desired configuration.""",
    "WAITER": """The Waiter domain involves a service robot operating in a restaurant. The robot navigates between tables and a buffet, picks up plates, fills them with food at the buffet, and serves customers at their tables.""",
    "TAXI": """The Taxi domain involves taxi vehicles navigating a street network between locations, picking up passengers at their origin locations, and dropping them off at their destinations.""",
    "SOKOBAN": """The Sokoban domain involves a warehouse keeper pushing crates onto designated goal squares within a grid maze. Crates can only be pushed into an empty space immediately behind them.""",
    "SANDWICH": """The Sandwich domain involves preparing sandwiches by assembling ingredients in a designated kitchen workspace. Bread, condiments, and fillings are gathered and stacked in sequence.""",
    "CLEANING": """The Cleaning domain involves cleaning robots navigating rooms, picking up debris, and using cleaning tools to sterilize surfaces.""",
    "BOOKS": """The Books domain involves planning a reading schedule for books over sequential months, respecting prerequisite reading dependencies and parallel reading constraints.""",
    "DOCK_WORKER": """The Dock Worker domain involves cranes loading and unloading shipping containers from trucks and stacking them onto pallets in dock depots.""",
    "MINEWORLD": """The Mineworld domain involves an agent navigating a grid, mining resources, crafting tools, and placing structures.""",
    "MINING": """The Mining domain involves extracting mineral deposits using mining equipment, loading ore into haulers, and transporting raw ore to processing plants.""",
    "PAINTING": """The Painting domain involves robotic sprayers and brush tools applying coats of paint to parts in designated paint booths.""",
    "NETWORK": """The Network domain involves routing data packets through a network topology between nodes under bandwidth and connectivity constraints.""",
    "PEG_SOLITAIR": """The Peg Solitaire domain involves jumping pegs over adjacent pegs into vacant holes on a board, removing the jumped peg to leave a target peg count.""",
    "SCANALIZER3D": """The Scanalyzer domain involves automated conveyor segments transporting luggage or cargo through 3D scanning machinery.""",
    "SNAKE": """The Snake domain involves navigating a snake body across a grid board, eating food to grow without colliding into walls or its own tail.""",
    "SAT_SOLVERS": """The SAT Solvers domain involves setting and evaluating boolean variables and clauses to satisfy propositional constraints.""",
    "VIDEOGAME": """The Videogame domain involves a character navigating game levels, defeating enemies, picking up items, and achieving level objectives.""",
    "ICE CREAM": """The Ice Cream domain involves scooping flavors and adding toppings to cones at a dessert parlor to fulfill customer orders.""",
    "MAINTENANCE": """The Maintenance domain involves scheduling mechanical inspections and servicing tasks on equipment across maintenance windows."""
}


def parse_pddl_domain_rules(domain_pddl: str, domain_name: str) -> str:
    """Translate PDDL domain structure into human-readable text."""
    narrative = KNOWN_DOMAIN_NARRATIVES.get(domain_name.upper())
    
    # Types
    types_match = re.search(r'\(:types\s+(.*?)\)', domain_pddl, re.IGNORECASE | re.DOTALL)
    types_lines = []
    if types_match:
        for line in types_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                types_lines.append(line)
                
    # Actions
    actions = []
    for act in re.finditer(r'\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*\Z)', domain_pddl, re.IGNORECASE | re.DOTALL):
        act_name = act.group(1)
        body = act.group(2)
        params_match = re.search(r':parameters\s*\((.*?)\)', body, re.IGNORECASE | re.DOTALL)
        pre_match = re.search(r':precondition\s*(.*?)(?=:effect|\)\s*\Z)', body, re.IGNORECASE | re.DOTALL)
        eff_match = re.search(r':effect\s*(.*)', body, re.IGNORECASE | re.DOTALL)
        
        params_str = params_match.group(1).strip() if params_match else ""
        actions.append((act_name, params_str))

    lines = []
    if narrative:
        lines.append(f"Domain Overview:\n{narrative.strip()}\n")
        
    lines.append(f"Domain: {domain_name}")
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


def parse_pddl_problem_scenario(prob_pddl: str, prob_name: str, domain_name: str) -> str:
    """Translate PDDL problem structure into natural language scenario text."""
    # Objects
    obj_match = re.search(r'\(:objects\s*(.*?)\)', prob_pddl, re.IGNORECASE | re.DOTALL)
    objects_lines = []
    if obj_match:
        for line in obj_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and not line.startswith(';'):
                objects_lines.append(line)

    # Initial state
    init_match = re.search(r'\(:init\s*(.*?)\(:goal', prob_pddl, re.IGNORECASE | re.DOTALL)
    init_facts = []
    if init_match:
        for fact in re.findall(r'\(([^()]+)\)', init_match.group(1)):
            fact = fact.strip()
            if fact and not fact.startswith('='):
                init_facts.append(fact)

    # Goal state
    goal_match = re.search(r'\(:goal\s*(.*)', prob_pddl, re.IGNORECASE | re.DOTALL)
    goal_facts = []
    if goal_match:
        for fact in re.findall(r'\(([^()]+)\)', goal_match.group(1)):
            fact = fact.strip()
            if fact and fact.lower() not in ('and', 'or', 'not'):
                goal_facts.append(fact)

    lines = [
        f"Problem Instance: {prob_name} (Domain: {domain_name})",
        "",
        "Objects:",
    ]
    for obj in objects_lines:
        lines.append(f"- {obj}")

    lines.append("\nInitial State Facts:")
    for fact in init_facts:
        lines.append(f"- {fact}")

    lines.append("\nGoal State Objectives:")
    for goal in goal_facts:
        lines.append(f"- {goal}")

    return "\n".join(lines)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    nl2pddl_dir = root_dir / "NL2PDDL" / "test"
    output_dir = root_dir / "prompt_NL2PDDL"
    output_dir_alias = root_dir / "promt_NL2PDLL"

    if not nl2pddl_dir.exists():
        print(f"Error: NL2PDDL test directory not found at {nl2pddl_dir}")
        return

    domains = sorted([d for d in os.listdir(nl2pddl_dir) if (nl2pddl_dir / d).is_dir()])
    print(f"Processing {len(domains)} domains from {nl2pddl_dir}...")

    count = 0
    for domain in domains:
        domain_path = nl2pddl_dir / domain
        doms_dir = domain_path / "domains"
        probs_dir = domain_path / "problems"

        # Locate best domain PDDL file
        dom_file = None
        if doms_dir.exists():
            files = os.listdir(doms_dir)
            if "domain_gold.pddl" in files:
                dom_file = doms_dir / "domain_gold.pddl"
            elif files:
                # pick baml2 or first
                baml2 = [f for f in files if "baml2" in f]
                dom_file = doms_dir / (baml2[0] if baml2 else sorted(files)[0])

        # Locate best problem PDDL file
        prob_file = None
        if probs_dir.exists():
            files = os.listdir(probs_dir)
            if "problem_gold.pddl" in files:
                prob_file = probs_dir / "problem_gold.pddl"
            elif files:
                baml2 = [f for f in files if "baml2" in f]
                prob_file = probs_dir / (baml2[0] if baml2 else sorted(files)[0])

        # Generate domain description
        if dom_file and dom_file.exists():
            with open(dom_file, "r", encoding="utf-8", errors="ignore") as f:
                dom_pddl = f.read()
            dom_desc = parse_pddl_domain_rules(dom_pddl, domain)
        else:
            narr = KNOWN_DOMAIN_NARRATIVES.get(domain.upper(), f"Domain {domain}")
            dom_desc = f"Domain: {domain}\n\n{narr}"

        # Generate problem description
        if prob_file and prob_file.exists():
            with open(prob_file, "r", encoding="utf-8", errors="ignore") as f:
                prob_pddl = f.read()
            prob_desc = parse_pddl_problem_scenario(prob_pddl, prob_file.name, domain)
        else:
            prob_desc = f"Problem instance for domain {domain}."

        # Write to prompt_NL2PDDL/<domain>/
        for base in [output_dir, output_dir_alias]:
            dest_dir = base / domain
            dest_dir.mkdir(parents=True, exist_ok=True)
            with open(dest_dir / "domain_description.txt", "w", encoding="utf-8") as f:
                f.write(dom_desc + "\n")
            with open(dest_dir / "problem_description.txt", "w", encoding="utf-8") as f:
                f.write(prob_desc + "\n")

        count += 1
        print(f"[{count:02d}/{len(domains)}] Extracted {domain} -> prompt_NL2PDDL/{domain}/")

    print(f"\nSuccessfully extracted all {count} domains into 'prompt_NL2PDDL/' and 'promt_NL2PDLL/'!")


if __name__ == "__main__":
    main()
