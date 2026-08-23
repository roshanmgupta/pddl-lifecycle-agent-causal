from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class LifecycleTaskType(str, Enum):
    ELICITATION = "ELICITATION"
    SYNTHETIC_FAULT_REPAIR = "SYNTHETIC_FAULT_REPAIR"
    DOMAIN_EVOLUTION = "DOMAIN_EVOLUTION"

class BenchmarkTask(BaseModel):
    """Schema for individual benchmark evaluation tasks in PDDLLifeCycleBench."""
    task_id: str = Field(
        description="Unique identifier for the benchmark task, e.g. 'blocksworld_repair_missing_precondition_01'"
    )
    domain_family: str = Field(
        description="IPC Domain family name: 'blocksworld', 'logistics', 'rovers', 'depots', 'satellite'"
    )
    task_type: LifecycleTaskType = Field(
        description="Lifecycle task category: ELICITATION, SYNTHETIC_FAULT_REPAIR, DOMAIN_EVOLUTION"
    )
    title: str = Field(
        description="Short human-readable summary of the evaluation scenario"
    )
    natural_language_requirements: str = Field(
        description="Natural language description of the domain rules or evolution requirements"
    )
    initial_domain_pddl: Optional[str] = Field(
        default=None,
        description="Starting domain PDDL text containing a fault (for REPAIR) or legacy spec (for EVOLUTION)"
    )
    initial_problem_pddl: Optional[str] = Field(
        default=None,
        description="Starting problem PDDL text (for REPAIR or EVOLUTION)"
    )
    fault_category: Optional[str] = Field(
        default=None,
        description="Injected fault category for REPAIR tasks: 'SYNTAX_PARSE', 'TYPE_SIGNATURE', 'GROUNDING_UNSOLVABILITY'"
    )
    ground_truth_domain_pddl: str = Field(
        description="Reference correct domain PDDL string for evaluation comparison"
    )
    ground_truth_problem_pddl: str = Field(
        description="Reference correct problem PDDL string for evaluation comparison"
    )
