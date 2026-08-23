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
        description="Evaluated agent architecture: 'ZERO_SHOT', 'UNSTRUCTURED_RETRY', 'CLOSED_LOOP_AST_AGENT'"
    )
    is_syntax_valid: bool = Field(
        default=False,
        description="True if compiled domain and problem PDDL pass VAL syntax and semantic validation"
    )
    is_plan_valid: bool = Field(
        default=False,
        description="True if Fast Downward classical planner finds a valid solution plan"
    )
    is_repaired: bool = Field(
        default=False,
        description="True if faulty model was successfully repaired to pass validation (for REPAIR tasks)"
    )
    iterations_used: int = Field(
        default=1,
        description="Number of repair iterations / feedback turns executed"
    )
    execution_time_seconds: float = Field(
        default=0.0,
        description="Total wall-clock runtime in seconds for task completion"
    )
    error_summary: Optional[str] = Field(
        default=None,
        description="Summary trace of remaining diagnostic errors if validation failed"
    )
