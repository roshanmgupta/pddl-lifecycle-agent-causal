import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

from benchmark.loader import load_benchmark_tasks
from benchmark.schema import LifecycleTaskType
from eval.benchmark_runner import run_benchmark_suite, generate_evaluation_report

def main():
    print("[START] Running PDDLLifeCycleBench Empirical Evaluation Pass...")
    
    # Load 3 representative benchmark tasks across task types
    eval_tasks = [
        load_benchmark_tasks(domain_family="blocksworld", task_type=LifecycleTaskType.ELICITATION)[0],
        load_benchmark_tasks(domain_family="blocksworld", task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR)[0],
        load_benchmark_tasks(domain_family="satellite", task_type=LifecycleTaskType.DOMAIN_EVOLUTION)[0]
    ]

    agent_architectures = ["ZERO_SHOT", "UNSTRUCTURED_RETRY", "CLOSED_LOOP_AST_AGENT"]

    metrics = run_benchmark_suite(eval_tasks, agent_architectures)
    
    report = generate_evaluation_report(metrics)
    
    print("\n" + "="*80)
    print(report)
    print("="*80)
    
    # Save report to scratch
    report_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "evaluation_report.md"))
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\n[SUCCESS]: Evaluation Report saved to: {report_file}")

if __name__ == "__main__":
    main()
