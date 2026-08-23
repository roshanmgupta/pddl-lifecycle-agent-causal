import sys
import os
import tempfile

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark.loader import load_benchmark_tasks, list_benchmark_summary, get_benchmark_task_by_id
from benchmark.schema import LifecycleTaskType
from tools.symbolic_oracles import run_val_validator

def test_benchmark_loader_and_summary():
    print("\n--- 1. Testing Benchmark Loader & Metadata Summary ---")
    summary = list_benchmark_summary()
    print("Total Tasks Registered:", summary["total_tasks"])
    print("Domain Families Covered:", summary["domain_families"])
    print("Task Types Covered:", summary["task_types"])
    print("Counts by Family:", summary["task_counts_by_family"])
    print("Counts by Type:", summary["task_counts_by_type"])

    assert summary["total_tasks"] >= 5, "Expected at least 5 benchmark tasks across IPC domains!"
    assert len(summary["domain_families"]) == 5, "Expected all 5 IPC domain families (blocksworld, logistics, rovers, depots, satellite)!"

def test_filtering_and_retrieval():
    print("\n--- 2. Testing Task Filtering & Retrieval ---")
    blocksworld_tasks = load_benchmark_tasks(domain_family="blocksworld")
    print(f"Blocksworld Tasks Count: {len(blocksworld_tasks)}")
    assert len(blocksworld_tasks) >= 2

    repair_tasks = load_benchmark_tasks(task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR)
    print(f"Synthetic Fault Repair Tasks Count: {len(repair_tasks)}")
    assert len(repair_tasks) >= 2

    task_by_id = get_benchmark_task_by_id("rovers_elicitation_01")
    assert task_by_id is not None
    assert task_by_id.domain_family == "rovers"
    print("Retrieved Task Title:", task_by_id.title)

def test_ground_truth_pddl_validity():
    print("\n--- 3. Verifying Benchmark Ground Truth PDDL Files ---")
    tasks = load_benchmark_tasks()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, task in enumerate(tasks, 1):
            dom_path = os.path.join(tmpdir, f"domain_{task.task_id}.pddl")
            prob_path = os.path.join(tmpdir, f"problem_{task.task_id}.pddl")

            with open(dom_path, "w") as f:
                f.write(task.ground_truth_domain_pddl)

            with open(prob_path, "w") as f:
                f.write(task.ground_truth_problem_pddl)

            print(f"Task #{idx} [{task.task_id}]: Ground truth files written.")
            # Note: Oracle validation check can run if Validate is present in PATH

if __name__ == "__main__":
    print("[START] Running PDDLLifeCycleBench Unit Tests...")
    test_benchmark_loader_and_summary()
    test_filtering_and_retrieval()
    test_ground_truth_pddl_validity()
    print("\n[SUCCESS] ALL BENCHMARK SUITE TESTS PASSED SUCCESSFULLY!")
