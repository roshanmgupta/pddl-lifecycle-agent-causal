from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class EvaluationMetrics(BaseModel):
    """Metrics recorded during a single benchmark task evaluation pass."""
    task_id: str = Field(
        description="Unique ID of the benchmark task evaluated"
    )
    domain_family: str = Field(
        description="IPC domain family, e.g., 'blocksworld', 'logistics', 'rovers'"
    )
    task_type: str = Field(
        description="Lifecycle task category: 'ELICITATION', 'SYNTHETIC_FAULT_REPAIR', 'DOMAIN_EVOLUTION'"
    )
    agent_type: str = Field(
        description="Evaluated agent architecture: 'ZERO_SHOT', 'UNSTRUCTURED_RETRY', 'CLOSED_LOOP_AST_AGENT', etc."
    )
    
    # -------------------------------------------------------------
    # 1. Primary Metric: End-to-End Verified Lifecycle Success
    # -------------------------------------------------------------
    e2e_success: bool = Field(
        default=False,
        description="True if domain & problem pass VAL, Fast Downward finds a plan, plan is certified by VAL, intended repair restored, and historical regression tests pass"
    )
    
    # -------------------------------------------------------------
    # 2. Secondary Correctness Metrics
    # -------------------------------------------------------------
    is_syntax_valid: bool = Field(
        default=False,
        description="True if compiled domain and problem PDDL pass VAL syntax and semantic validation"
    )
    is_plan_valid: bool = Field(
        default=False,
        description="True if Fast Downward classical planner finds a solution plan"
    )
    plan_execution_valid: bool = Field(
        default=False,
        description="True if VAL Validate.exe mathematically certifies that the plan reaches the goal"
    )
    is_repaired: bool = Field(
        default=False,
        description="True if faulty model was successfully repaired to pass validation & certification (for REPAIR tasks)"
    )
    
    # -------------------------------------------------------------
    # 3. Fault-Localization Metrics (Ranked Diagnostic Accuracy)
    # -------------------------------------------------------------
    fault_localization_top1: Optional[bool] = Field(
        default=None,
        description="True if Triage ranked the exact ground-truth faulty AST node at Rank 1"
    )
    fault_localization_top3: Optional[bool] = Field(
        default=None,
        description="True if ground-truth faulty AST node is present in top 3 ranked diagnostic reports"
    )
    fault_localization_mrr: Optional[float] = Field(
        default=None,
        description="Mean Reciprocal Rank (1/rank) of the true fault location in Triage diagnostic output"
    )

    # -------------------------------------------------------------
    # 4. Domain Evolution & Regression Metrics
    # -------------------------------------------------------------
    evolution_capability_valid: Optional[bool] = Field(
        default=None,
        description="True if new capability target problem was solved and certified"
    )
    regression_pass_rate: Optional[float] = Field(
        default=None,
        description="Fraction (0.0 to 1.0) of historical regression problems that remain solvable"
    )
    historical_problems_passed: Optional[int] = Field(
        default=None,
        description="Count of historical problem instances passed"
    )
    historical_problems_total: Optional[int] = Field(
        default=None,
        description="Total count of historical problem instances evaluated"
    )

    # -------------------------------------------------------------
    # 5. Efficiency & Computational Cost Metrics
    # -------------------------------------------------------------
    iterations_used: int = Field(
        default=1,
        description="Number of repair iterations / feedback turns executed"
    )
    execution_time_seconds: float = Field(
        default=0.0,
        description="Total wall-clock runtime in seconds for task completion"
    )
    total_tokens: int = Field(
        default=0,
        description="Total cumulative prompt + completion LLM tokens consumed"
    )
    token_efficiency_per_verified_domain: Optional[float] = Field(
        default=None,
        description="TEVD: Mean tokens consumed per verified domain (Göbel et al., 2026)"
    )
    repair_convergence_acceleration: Optional[float] = Field(
        default=None,
        description="RCA: Percentage reduction in repair iterations compared to unguided error backprompting"
    )
    estimated_cost_usd: float = Field(
        default=0.0,
        description="Estimated LLM API execution cost in USD"
    )
    error_summary: Optional[str] = Field(
        default=None,
        description="Summary trace of remaining diagnostic errors if validation failed"
    )

    # -------------------------------------------------------------
    # 6. Plan Quality Metrics
    # -------------------------------------------------------------
    plan_length: Optional[int] = Field(
        default=None,
        description="Number of plan action steps synthesized"
    )
    plan_cost: Optional[int] = Field(
        default=None,
        description="Metric cost of synthesized plan"
    )
    search_time: Optional[float] = Field(
        default=None,
        description="Fast Downward state search time in seconds"
    )
