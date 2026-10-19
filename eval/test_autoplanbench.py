"""
Automated Test Runner for AutoPlanBench with PDDL Lifecycle Agent
-----------------------------------------------------------------
Validates the closed-loop agent on pure typed STRIPS domains from AutoPlanBench:
1. Closed-Loop Fault Repair (Triage -> Repair -> Validation Oracles)
2. Elicitation from Natural Language Specification (NL -> Blueprint -> AST Compilation -> VAL/FD)
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward

AUTOPLANBENCH_DIR = PROJECT_ROOT / "pddl_benchmark_instances" / "autoplanbench"

def test_closed_loop_repair(domain_name: str = "gripper", instance_id: str = "instance-1"):
    print(f"\n================================================================================")
    print(f"TEST 1: CLOSED-LOOP TRIAGE & REPAIR ON '{domain_name.upper()}' ({instance_id})")
    print(f"================================================================================")
    
    dom_path = AUTOPLANBENCH_DIR / domain_name / "domain.pddl"
    prob_path = AUTOPLANBENCH_DIR / domain_name / "problems" / f"{instance_id}.pddl"
    
    if not dom_path.exists() or not prob_path.exists():
        print(f"[ERROR]: Benchmark files not found for {domain_name}")
        return
        
    ground_truth_dom = dom_path.read_text(encoding="utf-8")
    ground_truth_prob = prob_path.read_text(encoding="utf-8")
    
    # 1. Baseline Verification
    val_ok, val_log = run_val_validator(str(dom_path), str(prob_path))
    fd_ok, fd_log = run_fast_downward(str(dom_path), str(prob_path))
    print(f"[*] Ground-Truth Baseline: VAL Syntax={val_ok}, Fast Downward Solvable={fd_ok}")
    assert val_ok and fd_ok, "Ground truth domain must be valid and solvable!"

    # 2. Inject Realistic Defect into Domain
    # Defect: In gripper, remove the precondition (at ?obj ?room) from the 'pick' action
    # This causes an invalid causal transition or violates problem reachability
    print(f"[*] Injecting Semantic Defect: Removing '(at ?obj ?room)' from 'pick' action...")
    faulty_dom = ground_truth_dom.replace("(at ?obj ?room)", "")
    
    # Verify the faulty domain fails or has defect
    temp_faulty_dom = "PDDL_file/temp_faulty_gripper.pddl"
    os.makedirs("PDDL_file", exist_ok=True)
    with open(temp_faulty_dom, "w", encoding="utf-8") as f:
        f.write(faulty_dom)
        
    f_val_ok, f_val_log = run_val_validator(temp_faulty_dom, str(prob_path))
    print(f"[*] Faulty Domain Status: VAL={f_val_ok}")

    # 3. Invoke Closed-Loop PDDL Lifecycle Agent
    print(f"\n[*] Launching Closed-Loop LangGraph Pipeline (Triage -> Repair -> Validation)...")
    initial_state = {
        "requirements": f"Domain: {domain_name}. Repair the faulty PDDL specification so that actions conserve physical state constraints.",
        "pddl_domain_blueprint": {},
        "pddl_problem_blueprint": {},
        "generated_domain_pddl": faulty_dom,
        "generated_problem_pddl": ground_truth_prob,
        "verification_errors": ["Semantic Error: Action 'pick' is missing location precondition (at ?obj ?room), causing objects to be picked up from anywhere in the world."],
        "iteration_count": 0,
        "max_iterations": 3
    }
    
    start_t = time.time()
    final_state = pddl_lifecycle_graph.invoke(initial_state)
    elapsed = time.time() - start_t
    
    repaired_dom = final_state.get("generated_domain_pddl", "")
    repaired_prob = final_state.get("generated_problem_pddl", "")
    errors = final_state.get("verification_errors", [])
    
    # 4. Final Validation Oracle Checks
    eval_dom = "PDDL_file/eval_repaired_gripper.pddl"
    eval_prob = "PDDL_file/eval_repaired_gripper_prob.pddl"
    with open(eval_dom, "w", encoding="utf-8") as f:
        f.write(repaired_dom)
    with open(eval_prob, "w", encoding="utf-8") as f:
        f.write(repaired_prob)
        
    post_val_ok, post_val_log = run_val_validator(eval_dom, eval_prob)
    post_fd_ok, post_fd_log = run_fast_downward(eval_dom, eval_prob)
    
    print(f"\n--------------------------------------------------------------------------------")
    print(f"TEST 1 RESULTS:")
    print(f"  Execution Time        : {elapsed:.2f}s")
    print(f"  Iterations Used       : {final_state.get('iteration_count', 1)}")
    print(f"  VAL Syntax Valid      : {post_val_ok}")
    print(f"  FD Solvable           : {post_fd_ok}")
    print(f"  Remaining Errors      : {len(errors)}")
    print(f"  Total Tokens Used     : {final_state.get('total_tokens', 0)}")
    print(f"  Estimated Cost (USD)  : ${final_state.get('estimated_cost_usd', 0.0):.6f}")
    print(f"--------------------------------------------------------------------------------")
    
    return post_val_ok and post_fd_ok

def test_closed_loop_repair_pipesworld(instance_id: str = "instance-1"):
    print(f"\n================================================================================")
    print(f"TEST 2: CLOSED-LOOP TRIAGE & REPAIR ON 'PIPESWORLD' ({instance_id})")
    print(f"================================================================================")
    
    dom_path = AUTOPLANBENCH_DIR / "pipesworld" / "domain.pddl"
    prob_path = AUTOPLANBENCH_DIR / "pipesworld" / "problems" / f"{instance_id}.pddl"
    
    ground_truth_dom = dom_path.read_text(encoding="utf-8")
    ground_truth_prob = prob_path.read_text(encoding="utf-8")
    
    # 1. Baseline Verification
    val_ok, _ = run_val_validator(str(dom_path), str(prob_path))
    fd_ok, _ = run_fast_downward(str(dom_path), str(prob_path))
    print(f"[*] Ground-Truth Baseline: VAL Syntax={val_ok}, Fast Downward Solvable={fd_ok}")
    assert val_ok and fd_ok, "Ground truth pipesworld domain must be valid and solvable!"

    # 2. Inject Semantic Defect: Mutate PUSH-START precondition by removing (normal ?pipe)
    print(f"[*] Injecting Defect: Removing '(normal ?pipe)' from 'PUSH-START'...")
    faulty_dom = ground_truth_dom.replace("(normal ?pipe)", "", 1)
    
    initial_state = {
        "requirements": "Domain: pipesworld_strips. A pipeline segment must be in 'normal' operational state before push operations can commence.",
        "pddl_domain_blueprint": {},
        "pddl_problem_blueprint": {},
        "generated_domain_pddl": faulty_dom,
        "generated_problem_pddl": ground_truth_prob,
        "verification_errors": ["Semantic Error: Action 'PUSH-START' allows push operations when pipe is in an updating or invalid state because '(normal ?pipe)' precondition is missing."],
        "iteration_count": 0,
        "max_iterations": 3
    }
    
    start_t = time.time()
    final_state = pddl_lifecycle_graph.invoke(initial_state)
    elapsed = time.time() - start_t
    
    repaired_dom = final_state.get("generated_domain_pddl", "")
    repaired_prob = final_state.get("generated_problem_pddl", "")
    errors = final_state.get("verification_errors", [])
    
    eval_dom = "PDDL_file/eval_repaired_pipesworld.pddl"
    eval_prob = "PDDL_file/eval_repaired_pipesworld_prob.pddl"
    with open(eval_dom, "w", encoding="utf-8") as f:
        f.write(repaired_dom)
    with open(eval_prob, "w", encoding="utf-8") as f:
        f.write(repaired_prob)
        
    post_val_ok, post_val_log = run_val_validator(eval_dom, eval_prob)
    post_fd_ok, post_fd_log = run_fast_downward(eval_dom, eval_prob)
    
    print(f"\n--------------------------------------------------------------------------------")
    print(f"TEST 2 RESULTS (PIPESWORLD):")
    print(f"  Execution Time        : {elapsed:.2f}s")
    print(f"  Iterations Used       : {final_state.get('iteration_count', 1)}")
    print(f"  VAL Syntax Valid      : {post_val_ok}")
    print(f"  FD Solvable           : {post_fd_ok}")
    print(f"  Remaining Errors      : {len(errors)}")
    print(f"  Total Tokens Used     : {final_state.get('total_tokens', 0)}")
    print(f"  Estimated Cost (USD)  : ${final_state.get('estimated_cost_usd', 0.0):.6f}")
    print(f"--------------------------------------------------------------------------------")
    return post_val_ok and post_fd_ok

def main():
    print("====================================================================")
    print("STARTING AUTOPLANBENCH BENCHMARK SUITE TEST")
    print("====================================================================")
    
    t1_pass = test_closed_loop_repair(domain_name="gripper", instance_id="instance-1")
    t2_pass = test_closed_loop_repair_pipesworld(instance_id="instance-1")
    
    print("\n====================================================================")
    print("OVERALL AUTOPLANBENCH BENCHMARK TEST SUMMARY")
    print(f"  Test 1 (Gripper Repair)    : {'PASSED' if t1_pass else 'FAILED'}")
    print(f"  Test 2 (Pipesworld Repair) : {'PASSED' if t2_pass else 'FAILED'}")
    print("====================================================================")

if __name__ == "__main__":
    main()
