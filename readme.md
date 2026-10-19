# Towards an Autonomous Lifecycle Agent for PDDL Domain Modelling

> **Master's Thesis Project**  
> **Author**: Roshan Gupta  
> **Supervisor**: Prof. Dr. Ilche Georgievski  
> **Institution**: Institute of Architecture of Application Systems (IAAS), University of Stuttgart  
> **License**: MIT  

---

## 📌 Project Overview

Constructing robust, error-free **PDDL (Planning Domain Definition Language)** domain models for classical automated planning is a complex, iterative process. Traditional approaches treat PDDL creation as an isolated, single-shot natural language translation task, which frequently leads to syntax errors, arity mismatches, and unreachable state deadlocks.

This project implements an **Autonomous Closed-Loop Lifecycle Agent** for classical planning (strictly pure **PDDL 2.1** with `:strips` and `:typing`). Rather than emitting raw Lisp code directly from stochastic prompts, the agent orchestrates the complete software engineering lifecycle:

1. **Phase 1: Requirements Elicitation** — Extracts structured semantics from natural language into a strongly typed Pydantic intermediate representation (`DomainBlueprint` and `ProblemBlueprint`).
2. **Phase 2: Deterministic Compilation** — Compiles the validated Abstract Syntax Tree (AST) schema into 100% syntactically valid PDDL 2.1 Lisp code via a deterministic Python compiler.
3. **Phase 3: Symbolic Verification, Diagnostic Triage & Repair** — Couples formal symbolic oracles (**VAL** for grammar/plan validation and **Fast Downward** for search reachability) with Spectrum-Based Fault Localization (**SBFL** using the Ochiai coefficient) and SAS+ Causal Graph traversal to localize and surgically repair domain bugs.
4. **Phase 4: Continuous Domain Evolution & Regression Gatekeeping** — Extends existing domain capabilities while enforcing a mandatory historical regression test suite to mathematically prevent backward-compatibility regressions (catastrophic forgetting).

---

## 📂 Repository Directory Structure

```text
pddl_lifecycle_agent/
├── app.py                             # Interactive Streamlit application
├── graph.py                           # LangGraph state machine orchestrating the closed-loop lifecycle
├── requirements.txt                   # Python package dependencies
├── .env.example                       # Example environment file for API keys and model configuration
│
├── nodes/                             # Implementation of the 5 KEPS lifecycle nodes
│   ├── elicitation.py                 # Node 1: Natural language extraction into AST blueprints
│   ├── generation.py                  # Node 2: Deterministic Python-to-PDDL Lisp compiler
│   ├── triage.py                      # Node 4: Layered diagnostic error categorization & SBFL ranking
│   ├── repair.py                      # Node 5: Targeted, surgical AST blueprint repair
│   └── maintenance.py                 # Node 6: Phase 4 historical regression testing gatekeeper
│
├── schemas/                           # Strongly typed Pydantic intermediate representations
│   └── pddl_blueprint.py              # DomainBlueprint and ProblemBlueprint schemas
│
├── config/                            # Standards and execution configurations
│   ├── model_config.py                # Strict phase-to-model LLM mapping
│   └── pddl_standards.py              # Classical PDDL 2.1 STRIPS and typing rules
│
├── tools/                             # Symbolic oracles and analysis tools
│   ├── symbolic_oracles.py            # Subprocess wrappers for VAL (Validate.exe) & Fast Downward
│   ├── sbfl_analyzer.py               # Spectrum-Based Fault Localization (Ochiai & Tarantula)
│   ├── blueprint_parser.py            # Bidirectional PDDL-to-Blueprint parser
│   └── benchmark_loader.py            # Task and domain loader for PDDLLifeCycleBench
│
├── eval/                              # Evaluation methodology, baselines, and benchmarking
│   ├── metrics.py                     # Formal Pydantic metrics definitions (SVR, PVR, RSR, RPR, etc.)
│   ├── benchmark_runner.py            # Automated benchmark evaluation orchestrator
│   ├── baselines.py                   # Zero-shot direct & unstructured iterative retry baselines
│   └── run_ipc_evaluation.py          # Batch runner for multi-domain benchmark experiments
│
├── benchmark/                         # Benchmark datasets, loaders, and schemas
│   ├── dataset.py                     # Benchmark task dataset structures
│   ├── loader.py                      # IPC and AutoPlanBench instance loaders
│   └── schema.py                      # Benchmark task metadata schemas
│
├── PDDLLifeCycleBench/                # Curated benchmark suite (24 domains, 120 tasks)
│   ├── barman14-bfs/                  # Robotics & mixing domain instances & flaws
│   ├── blocksworld/                   # Stacking & causal dependency instances & flaws
│   ├── gripper/                       # Multi-gripper robotic transport
│   ├── logistics/                     # Freight logistics transport
│   └── ... (24 canonical IPC domain directories)
│
├── tests/                             # Automated pytest test suite
│   ├── test_compiler.py               # Tests for deterministic PDDL generation
│   ├── test_oracles.py                # Tests for VAL and Fast Downward execution
│   └── test_sbfl.py                   # Tests for fault localization scoring
│
└── docs/                              # Project documentation and specifications
    ├── SYSTEM_ARCHITECTURE_SPEC.md    # Formal system architecture specification
    ├── QUESTION_ANSWERS.md            # Comprehensive thesis defense and technical Q&A
    └── PENDING_BATCH_METRICS_CALCULATION.md # Cross-domain batch metrics tracking
```

---

## 🛠️ Prerequisites

Before installing the project, ensure your environment meets the following requirements:

1. **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS.
2. **Python**: Python **3.10** or higher (Conda recommended).
3. **Symbolic Planning Oracles**:
   - **VAL (Plan Validation Tool)**: `Validate.exe` (Windows) or `validate` (Linux/macOS) must be placed in `tools/bin/` or added to your system `PATH`.
   - **Fast Downward**: A working Fast Downward installation (`fast-downward.py`) must be accessible via system `PATH` or configured in your environment.
4. **LLM Provider**:
   - An active **OpenRouter** API key (`OPENROUTER_API_KEY`). All LLM inference calls are routed through OpenRouter to ensure deterministic model assignment and reproducibility.

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/roshanmgupta/pddl-lifecycle-agent.git
cd pddl-lifecycle-agent
```

### 2. Create and Activate a Virtual Environment

Using Conda (Recommended):
```bash
conda create -n agent_env python=3.10 -y
conda activate agent_env
```

Using standard `venv`:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
# Required: OpenRouter API Key
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Strict Phase-to-Model Assignments
LLM_PHASE_1=deepseek/deepseek-chat
LLM_PHASE_3=deepseek/deepseek-chat
LLM_PHASE_4=deepseek/deepseek-chat

# Oracle Executable Paths (Optional: configure if not on system PATH)
VAL_PATH=tools/bin/Validate.exe
FAST_DOWNWARD_PATH=fast-downward.py
```

---

## 💻 Running the Application

### 1. Launch the Interactive Streamlit UI
To start the multi-tab interactive interface for domain elicitation, fault repair, and evolution:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. From the UI, you can:
- Select from 24 canonical domains and 120 benchmark tasks across Categories A, B, and C.
- Choose between the proposed `CLOSED_LOOP_AST_AGENT` and comparative baselines (Zero-Shot Direct, Unstructured Retry).
- Inspect compiled PDDL code, step-by-step action plans, AST blueprints, diagnostic triage reports, and formal metric scorecards.

### 2. Run Automated Batch Evaluation
To run automated batch evaluation across benchmark domains:
```bash
python -m eval.run_ipc_evaluation --systems CLOSED_LOOP_AST_AGENT,UNSTRUCTURED_RETRY,ZERO_SHOT
```

### 3. Run Automated Unit Tests
```bash
pytest tests/
```

---

## 📊 Evaluation Metrics (PDDLLifeCycleBench)

The system automatically measures formal metrics grounded in symbolic oracles:
- **Syntax Validity Rate (SVR)**: Percentage of emitted domains parsed without syntax errors via VAL.
- **Solvability Rate (SR)**: Percentage of tasks where Fast Downward finds a reachable action sequence.
- **Plan Validity Rate (PVR)**: Percentage of tasks where VAL mathematically certifies every state transition from initial state to goal.
- **Repair Success Rate (RSR)**: Percentage of flawed domains successfully repaired within a maximum of 10 iterations.
- **Fault Localisation Accuracy (FLA)**: Top-1 accuracy and Mean Reciprocal Rank (MRR) of identifying the ground-truth faulty action schema.
- **Regression Pass Rate (RPR)**: Percentage of historical legacy problems preserved post-evolution.
- **Repair Convergence Acceleration (RCA)**: Percentage iteration reduction achieved by triage over naive re-prompting.
- **Token Efficiency per Verified Domain (TEVD)**: Inference tokens consumed per verified, working domain deliverable.

---

## 📄 License & Academic Attribution

This project is licensed under the **MIT License**.

If you use this codebase or benchmark suite in your research, please cite:
```bibtex
@mastersthesis{gupta2026pddllifecycle,
  author       = {Roshan Gupta},
  title        = {Towards an Autonomous Lifecycle Agent for PDDL Domain Modelling},
  school       = {Institute of Architecture of Application Systems (IAAS), University of Stuttgart},
  year         = {2026},
  supervisor   = {Prof. Dr. Ilche Georgievski}
}
```
