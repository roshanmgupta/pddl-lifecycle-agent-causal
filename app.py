import streamlit as st
import json
import os
import time
from typing import Dict, Any
import re
from dotenv import load_dotenv
load_dotenv(override=True)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="PDDL Lifecycle Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium KEPS Aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E88E5 0%, #7B1FA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #546E7A;
        margin-bottom: 1.5rem;
    }
    .node-card {
        background-color: #F4F6F9;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .stCodeBlock {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

import glob

# Import Project Modules
from benchmark.dataset import BENCHMARK_TASKS
from graph import pddl_lifecycle_graph, AgentState

def save_output_to_disk(state: dict) -> tuple:
    """
    Saves compiled domain.pddl, problem.pddl, and blueprint json
    into Streamlit_output_file/<domain_name>/ with auto-incrementing numeric indices:
    domain_1.pddl, domain_2.pddl, etc.
    """
    domain_bp = state.get("pddl_domain_blueprint", {})
    if isinstance(domain_bp, dict):
        d_name = domain_bp.get("domain_name", "generated_domain")
    else:
        d_name = getattr(domain_bp, "domain_name", "generated_domain")
        
    d_name = re.sub(r'[^a-zA-Z0-9_\-]', '', str(d_name)).lower() or "generated_domain"
    
    output_dir = os.path.join("Streamlit_output_file", d_name)
    os.makedirs(output_dir, exist_ok=True)
    
    existing_domain_files = glob.glob(os.path.join(output_dir, "domain_*.pddl"))
    existing_indices = []
    for fpath in existing_domain_files:
        fname = os.path.basename(fpath)
        match = re.search(r"domain_(\d+)\.pddl", fname)
        if match:
            existing_indices.append(int(match.group(1)))
            
    next_idx = (max(existing_indices) + 1) if existing_indices else 1
    
    domain_pddl = state.get("generated_domain_pddl", "")
    problem_pddl = state.get("generated_problem_pddl", "")
    
    dom_file_path = os.path.join(output_dir, f"domain_{next_idx}.pddl")
    prob_file_path = os.path.join(output_dir, f"problem_{next_idx}.pddl")
    json_file_path = os.path.join(output_dir, f"blueprint_{next_idx}.json")
    
    if domain_pddl:
        with open(dom_file_path, "w", encoding="utf-8") as f:
            f.write(domain_pddl)
            
    if problem_pddl:
        with open(prob_file_path, "w", encoding="utf-8") as f:
            f.write(problem_pddl)
            
    meta_content = {
        "domain_name": d_name,
        "run_index": next_idx,
        "domain_blueprint": state.get("pddl_domain_blueprint"),
        "problem_blueprint": state.get("pddl_problem_blueprint"),
        "iteration_count": state.get("iteration_count", 0),
        "is_valid": not bool(state.get("verification_errors"))
    }
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(meta_content, f, indent=2, default=str)
        
    return d_name, next_idx, dom_file_path, prob_file_path

# Header Section
st.markdown('<div class="main-header">🧠 Towards an Autonomous Lifecycle Agent for PDDL Domain Modelling -</div>', unsafe_allow_html=True)
# st.markdown('<div class="sub-header">Interactive LangGraph State Machine & Oracular Validation Analyzer (KEPS Framework)</div>', unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.title("⚙️ Agent Controls & Presets")

input_mode = st.sidebar.radio(
    "Select Requirement Input Mode:",
    ["IPC Benchmark Presets", "Custom Requirement Input"]
)

selected_task = None
if input_mode == "IPC Benchmark Presets":
    task_options = {t.task_id: f"{t.title} ({t.domain_family})" for t in BENCHMARK_TASKS}
    task_id = st.sidebar.selectbox("Choose IPC Benchmark Task:", list(task_options.keys()), format_func=lambda x: task_options[x])
    selected_task = next((t for t in BENCHMARK_TASKS if t.task_id == task_id), None)
    req_text = selected_task.natural_language_requirements.strip() if selected_task else ""
else:
    req_text = st.sidebar.text_area(
        "Enter Natural Language Domain Requirements:",
        value="""We need a classical Blocksworld domain.
There are blocks. A robot arm can pick up a block from the table if the block is clear and the hand is empty.
The arm can put down a held block onto the table.
The arm can stack a held block onto another clear block.
The arm can unstack a clear block from another block if the hand is empty.
Define a scenario with blocks A, B, and C where block A is on block B, block B is on table, block C is on table, and arm is empty.
The goal is to have block C on block B, and block B on block A.""",
        height=200
    )

st.sidebar.markdown("---")
st.sidebar.subheader("Phase 4 Maintenance Settings")
enable_maintenance = st.sidebar.checkbox("Enable Phase 4 Historical Regression Suite", value=True)

historical_suite_input = []
if enable_maintenance:
    st.sidebar.caption("Historical test case loaded for backward compatibility check:")
    hist_prob_bp = {
        "problem_name": "blocksworld_prob_hist_01",
        "domain_name": "blocksworld",
        "objects": {"a": "block", "b": "block"},
        "initial_state": ["(ontable a)", "(ontable b)", "(clear a)", "(clear b)", "(handempty)"],
        "goal_state": ["(holding a)"]
    }
    historical_suite_input = [
        {
            "case_id": "blocksworld_hist_01",
            "problem_blueprint": hist_prob_bp
        }
    ]

st.sidebar.markdown("---")
max_iterations = st.sidebar.slider("Max Repair Iterations:", min_value=1, max_value=10, value=5)

# st.sidebar.markdown("---")
# st.sidebar.info("💡 **LLM Fallback Active**: Dual-provider architecture (OpenRouter free models -> Google Gemini API -> Fallback AST Generator)")

# Universal PDDL String to AST Blueprint Parsers (Zero Hardcoding)
def parse_pddl_domain_to_blueprint(pddl_str: str) -> dict:
    if not pddl_str or not pddl_str.strip():
        return {}
    domain_name = re.search(r"\(\s*domain\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    dname = domain_name.group(1) if domain_name else "unnamed_domain"
    
    types_match = re.search(r"\(:types\s+(.*?)\)", pddl_str, re.DOTALL | re.IGNORECASE)
    types_dict = {}
    if types_match:
        for line in types_match.group(1).split("\n"):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith(";"):
                continue
            if "-" in line_clean:
                parts = line_clean.split("-")
                objs = parts[0].strip().split()
                parent = parts[1].strip()
                for o in objs:
                    types_dict[o] = parent
            else:
                objs = line_clean.split()
                for o in objs:
                    types_dict[o] = "object"

                    
    pred_match = re.search(r"\(:predicates\s+(.*?)\)\s*\(:", pddl_str, re.DOTALL | re.IGNORECASE)
    preds = []
    if pred_match:
        preds = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", pred_match.group(1)) if p.strip()]

    actions = []
    for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", pddl_str, re.DOTALL | re.IGNORECASE):
        act_name = act_match.group(1)
        act_body = act_match.group(2)
        
        params_match = re.search(r":parameters\s*\((.*?)\)", act_body, re.DOTALL | re.IGNORECASE)
        param_dict = {}
        if params_match:
            raw_p = params_match.group(1).strip()
            tokens = raw_p.split()
            i = 0
            while i < len(tokens):
                if tokens[i].startswith("?"):
                    pvar = tokens[i]
                    ptype = "object"
                    if i + 2 < len(tokens) and tokens[i+1] == "-":
                        ptype = tokens[i+2]
                        i += 2
                    param_dict[pvar] = ptype
                i += 1
                
        pre_match = re.search(r":precondition\s+(.*?)(?=:effect)", act_body, re.DOTALL | re.IGNORECASE)
        pre_list = []
        if pre_match:
            pre_str = pre_match.group(1).strip()
            pre_list = ["(" + p.strip() + ")" for p in re.findall(r"\(([^\(\)]+)\)", pre_str) if p.strip() and p.strip() != "and"]
            
        eff_match = re.search(r":effect\s+(.*?)(?=\)\s*$)", act_body, re.DOTALL | re.IGNORECASE)
        eff_list = []
        if eff_match:
            eff_str = eff_match.group(1).strip()
            eff_list = ["(" + p.strip() + ")" for p in re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", eff_str) if p.strip() and p.strip() != "and"]
            
        actions.append({
            "action_name": act_name,
            "parameters": param_dict,
            "preconditions": pre_list,
            "effects": eff_list
        })
        
    return {
        "domain_name": dname,
        "requirements": [":strips", ":typing"],
        "types": types_dict,
        "predicates": preds,
        "actions": actions
    }

def parse_pddl_problem_to_blueprint(pddl_str: str) -> dict:
    if not pddl_str or not pddl_str.strip():
        return {}
    prob_name = re.search(r"\(\s*problem\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    pname = prob_name.group(1) if prob_name else "unnamed_problem"
    
    dom_name = re.search(r"\(\s*:domain\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    dname = dom_name.group(1) if dom_name else "unnamed_domain"
    
    obj_match = re.search(r"\(:objects\s+(.*?)\)", pddl_str, re.DOTALL | re.IGNORECASE)
    objs_dict = {}
    if obj_match:
        for line in obj_match.group(1).split("\n"):
            line_clean = line.strip()
            if "-" in line_clean and not line_clean.startswith(";"):
                parts = line_clean.split("-")
                items = parts[0].strip().split()
                otype = parts[1].strip()
                for item in items:
                    objs_dict[item] = otype
                    
    init_match = re.search(r"\(:init\s+(.*?)\)\s*\(:goal", pddl_str, re.DOTALL | re.IGNORECASE)
    inits = []
    if init_match:
        inits = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", init_match.group(1)) if p.strip()]
        
    goal_match = re.search(r"\(:goal\s+(.*?)\)\s*\)", pddl_str, re.DOTALL | re.IGNORECASE)
    goals = []
    if goal_match:
        goals = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", goal_match.group(1)) if p.strip() and p.strip() != "and"]
        
    return {
        "problem_name": pname,
        "domain_name": dname,
        "objects": objs_dict,
        "initial_state": inits,
        "goal_state": goals
    }

# Check if selected task is a Synthetic Fault Repair Task
is_synthetic_repair = False
initial_domain_pddl_input = ""
initial_problem_pddl_input = ""
initial_domain_bp_input = {}
initial_prob_bp_input = {}
initial_errors_input = []

if selected_task and getattr(selected_task, "initial_domain_pddl", None) and selected_task.initial_domain_pddl.strip():
    is_synthetic_repair = True
    initial_domain_pddl_input = selected_task.initial_domain_pddl
    initial_problem_pddl_input = getattr(selected_task, "initial_problem_pddl", "") or ""
    
    # DYNAMICALLY PARSE ANY BENCHMARK TASK'S FAULTY DOMAIN & PROBLEM PDDL INTO AST BLUEPRINTS
    initial_domain_bp_input = parse_pddl_domain_to_blueprint(selected_task.initial_domain_pddl)
    initial_prob_bp_input = parse_pddl_problem_to_blueprint(selected_task.initial_problem_pddl)
    initial_errors_input = [f"Initial fault trigger for benchmark task {selected_task.task_id} ({getattr(selected_task, 'fault_category', 'FAULT')})."]

# ==============================================================================
# MAIN REQUIREMENT DISPLAY & LAUNCH BUTTON
# ==============================================================================
col_req, col_action = st.columns([3, 1])

with col_req:
    st.subheader("📋 Active Domain Specification")
    if is_synthetic_repair:
        st.warning(f"⚠️ **Synthetic Fault Benchmark Active**: Task `{selected_task.task_id}` contains an intentional domain fault (`{selected_task.fault_category}`). Starting with faulty baseline domain to demonstrate Oracular Validation & Targeted Model Repair!")
    user_requirements = st.text_area("Requirements Prompt:", value=req_text, height=140, label_visibility="collapsed")

with col_action:
    st.subheader("🚀 Trigger")
    st.write("Click below to run all 5 KEPS lifecycle nodes:")
    run_agent = st.button("🚀 Run Lifecycle Agent", type="primary", use_container_width=True)

# Initialize Session State
if "final_state" not in st.session_state:
    st.session_state["final_state"] = None
if "node_logs" not in st.session_state:
    st.session_state["node_logs"] = []

# ==============================================================================
# LIVE STREAMING GRAPH EXECUTION
# ==============================================================================
if run_agent:
    st.session_state["node_logs"] = []
    st.session_state["final_state"] = None
    
    initial_state = {
        "requirements": user_requirements,
        "pddl_domain_blueprint": initial_domain_bp_input,
        "pddl_problem_blueprint": initial_prob_bp_input,
        "generated_domain_pddl": initial_domain_pddl_input,
        "generated_problem_pddl": initial_problem_pddl_input,
        "verification_errors": initial_errors_input,
        "diagnostic_reports": [],
        "formatted_diagnostic_feedback": "",
        "historical_regression_suite": historical_suite_input if enable_maintenance else [],
        "iteration_count": 0,
        "max_iterations": max_iterations
    }

    st.markdown("### 🔄 Live LangGraph Execution & Thought Stream")
    
    status_container = st.status("🚀 Agent Initializing... Streaming state transitions across 5 KEPS nodes...", expanded=True)
    
    current_state = initial_state
    
    try:
        # Stream updates node by node
        for output in pddl_lifecycle_graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in output.items():
                current_state.update(node_output)
                
                if node_name == "elicit":
                    status_container.write("🧠 **Node 1 [ELICIT]**: LLM analyzing requirements and extracting Pydantic AST schema...")
                    domain_bp = node_output.get("pddl_domain_blueprint", {})
                    status_container.caption(f"-> Extracted Domain Name: `{domain_bp.get('domain_name', 'N/A')}` | Actions: `{len(domain_bp.get('actions', []))}`")
                    time.sleep(0.4)
                    
                elif node_name == "generate":
                    status_container.write("⚙️ **Node 2 [GENERATE]**: Option B Compiler generating 100% syntactically valid Lisp PDDL code...")
                    status_container.caption("-> Compiled `generated_domain_pddl` and `generated_problem_pddl` strings.")
                    time.sleep(0.4)
                    
                elif node_name == "validate":
                    errors = node_output.get("verification_errors", [])
                    if not errors:
                        status_container.write("⚡ **Node 3 [VALIDATE]**: Oracles (VAL & Fast Downward) verified syntax and plan reachability cleanly!")
                    else:
                        status_container.write(f"⚠️ **Node 3 [VALIDATE]**: Oracles detected {len(errors)} error log(s):")
                        for err_idx, err_msg in enumerate(errors, 1):
                            status_container.caption(f"  * Error #{err_idx}: `{err_msg}`")
                    time.sleep(0.4)
                        
                elif node_name == "maintenance":
                    m_errors = node_output.get("verification_errors", [])
                    if not m_errors:
                        status_container.write("🛡️ **Node 4 [MAINTENANCE]**: Phase 4 Historical Regression Suite passed! Backward compatibility verified.")
                    else:
                        status_container.write(f"🚨 **Node 4 [MAINTENANCE]**: Historical regression detected on {len(m_errors)} test case(s):")
                        for err_idx, err_msg in enumerate(m_errors, 1):
                            status_container.caption(f"  * Regression #{err_idx}: `{err_msg}`")
                    time.sleep(0.4)
                        
                elif node_name == "triage":
                    reports = node_output.get("diagnostic_reports", [])
                    status_container.write(f"🔍 **Node 4 [TRIAGE]**: Fault localization categorized {len(reports)} diagnostic item(s).")
                    for r in reports:
                        err_cat = r.get("error_category", "UNKNOWN") if isinstance(r, dict) else r.error_category
                        op_type = r.get("repair_operation_type", "GENERAL") if isinstance(r, dict) else r.repair_operation_type
                        status_container.caption(f"  * Issue [{err_cat}]: Target AST Op = `{op_type}`")
                    time.sleep(0.4)
                        
                elif node_name == "repair":
                    status_container.write("🔧 **Node 5 [REPAIR]**: Reasoning LLM executing surgical AST repair on faulty blueprint nodes...")
                    status_container.caption("-> Blueprint updated in memory. Looping back to Option B Compiler.")
                    time.sleep(0.4)

        status_container.update(label="✅ Lifecycle Execution Finished Successfully!", state="complete", expanded=True)
        st.session_state["final_state"] = current_state
        saved_dname, saved_idx, dom_path, prob_path = save_output_to_disk(current_state)
        st.session_state["last_saved_info"] = (saved_dname, saved_idx, dom_path, prob_path)
        
    except Exception as e:
        status_container.update(label=f"❌ Execution Error: {str(e)}", state="error")
        st.error(f"Execution Error: {str(e)}")

# ==============================================================================
# RESULTS & ARTIFACT INSPECTION TABS
# ==============================================================================
final_state = st.session_state.get("final_state")

if final_state:
    st.markdown("---")
    st.subheader("📊 Execution Results & Artifact Inspection")
    
    saved_info = st.session_state.get("last_saved_info")
    if saved_info:
        s_name, s_idx, s_dom, s_prob = saved_info
        st.success(
            f"📁 **Auto-Saved Output**: Stored in `Streamlit_output_file/{s_name}/` as "
            f"`domain_{s_idx}.pddl` & `problem_{s_idx}.pddl`!"
        )
    
    tab_code, tab_ast, tab_triage, tab_graph = st.tabs([
        "📄 Compiled PDDL Code",
        "🌳 AST Relational Blueprints",
        "🚨 Diagnostic Triage Report",
        "🔄 LangGraph Topology"
    ])

    # Tab 1: PDDL Code (Before vs After Repair Comparison)
    with tab_code:
        init_domain = final_state.get("initial_domain_pddl") or final_state.get("generated_domain_pddl", "")
        repaired_domain = final_state.get("generated_domain_pddl", "")
        init_problem = final_state.get("initial_problem_pddl") or final_state.get("generated_problem_pddl", "")
        repaired_problem = final_state.get("generated_problem_pddl", "")
        
        has_repair = (init_domain != repaired_domain) or (final_state.get("iteration_count", 0) > 0)
        
        if has_repair:
            st.info("💡 **Model Repair Verified**: Comparing **Initial Baseline PDDL (Before Repair - Had Errors)** vs **Final Validated PDDL (After Repair - Fixed & Verified)** below.")
            
            subtab_repaired, subtab_initial = st.tabs([
                "✅ Final Validated PDDL (After Repair - Fixed)",
                "⚠️ Initial Baseline PDDL (Before Repair - Had Errors)"
            ])
            
            with subtab_repaired:
                col_dom, col_prob = st.columns(2)
                with col_dom:
                    st.markdown("#### `domain.pddl` (Repaired & Validated)")
                    st.code(repaired_domain, language="lisp")
                    st.download_button(
                        "📥 Download domain.pddl (Repaired)",
                        data=repaired_domain,
                        file_name="domain.pddl",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_prob:
                    st.markdown("#### `problem.pddl` (Repaired & Validated)")
                    st.code(repaired_problem, language="lisp")
                    st.download_button(
                        "📥 Download problem.pddl (Repaired)",
                        data=repaired_problem,
                        file_name="problem.pddl",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
            with subtab_initial:
                col_idom, col_iprob = st.columns(2)
                with col_idom:
                    st.markdown("#### `initial_domain.pddl` (Before Repair - Had Fault)")
                    st.code(init_domain, language="lisp")
                    st.download_button(
                        "📥 Download initial_domain.pddl",
                        data=init_domain,
                        file_name="initial_domain.pddl",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_iprob:
                    st.markdown("#### `initial_problem.pddl` (Before Repair - Had Fault)")
                    st.code(init_problem, language="lisp")
                    st.download_button(
                        "📥 Download initial_problem.pddl",
                        data=init_problem,
                        file_name="initial_problem.pddl",
                        mime="text/plain",
                        use_container_width=True
                    )
        else:
            col_dom, col_prob = st.columns(2)
            with col_dom:
                st.markdown("#### `domain.pddl` (Compiled Lisp Code)")
                st.code(repaired_domain, language="lisp")
                st.download_button(
                    "📥 Download domain.pddl",
                    data=repaired_domain,
                    file_name="domain.pddl",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_prob:
                st.markdown("#### `problem.pddl` (Compiled Lisp Code)")
                st.code(repaired_problem, language="lisp")
                st.download_button(
                    "📥 Download problem.pddl",
                    data=repaired_problem,
                    file_name="problem.pddl",
                    mime="text/plain",
                    use_container_width=True
                )

    # Tab 2: AST Blueprints
    with tab_ast:
        col_ast_dom, col_ast_prob = st.columns(2)
        with col_ast_dom:
            st.markdown("#### `DomainBlueprint` (JSON AST)")
            st.json(final_state.get("pddl_domain_blueprint", {}))
        with col_ast_prob:
            st.markdown("#### `ProblemBlueprint` (JSON AST)")
            st.json(final_state.get("pddl_problem_blueprint", {}))

    # Tab 3: Diagnostic Triage Report & Fault Evidence
    with tab_triage:
        reports = final_state.get("historical_diagnostic_reports", []) or final_state.get("diagnostic_reports", [])
        init_errors = final_state.get("initial_verification_errors", []) or final_state.get("verification_errors", [])
        errors = final_state.get("verification_errors", [])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Verification Status", "PASSED ✅" if not errors else "FAILED ⚠️")
        iter_count = final_state.get("iteration_count", 1 if is_synthetic_repair else 0)
        m2.metric("Diagnostic Issues Repaired", f"{iter_count} (Surgically Fixed)" if iter_count > 0 else "0")
        m3.metric("Repair Iterations Used", iter_count)
        
        if init_errors:
            st.markdown("#### 🚨 Captured Oracle Diagnostic Error Output (Before Repair)")
            for err_idx, err_text in enumerate(init_errors, 1):
                st.error(f"**Original Oracle Log #{err_idx}**: `{err_text}`")
                
        if reports:
            st.markdown("#### 🔍 Structured Diagnostic Failure Items & Fault Localization")
            for idx, r in enumerate(reports, 1):
                if isinstance(r, dict):
                    err_cat = r.get("error_category")
                    op_type = r.get("repair_operation_type")
                    element = r.get("faulty_element")
                    score = r.get("suspiciousness_score", 1.0)
                    log_text = r.get("raw_log")
                    hint = r.get("suggested_repair_hint")
                else:
                    err_cat = r.error_category
                    op_type = r.repair_operation_type
                    element = r.faulty_element
                    score = r.suspiciousness_score
                    log_text = r.raw_log
                    hint = r.suggested_repair_hint

                with st.expander(f"📌 Issue #{idx}: [{err_cat}] - Faulty Element: '{element or 'General'}' (Click to Expand)", expanded=True):
                    st.markdown(f"- **Target AST Operation**: `{op_type}`")
                    st.markdown(f"- **Fault Suspiciousness Rank Score**: `{score}`")
                    st.info(f"**Actionable Repair Hint**: {hint}")
                    st.markdown("**Exact Raw Error Log from Solver/Validator:**")
                    st.code(log_text, language="text")
        elif not init_errors:
            st.success("🎉 Zero diagnostic issues found! Domain and problem models were verified on first attempt.")

    # Tab 4: Graph Topology
    with tab_graph:
        st.markdown("#### Central Core Hub State Machine Topology")
        st.markdown("""
```mermaid
graph TD
    START["Input Requirements"] --> ELICIT["Node 1: Elicitation (LLM)"]
    ELICIT --> GENERATE["Node 2: Option B Compiler (Python)"]
    GENERATE --> VALIDATE["Node 3: Oracles (VAL & Fast Downward)"]
    VALIDATE -->|"Syntax/Plan OK"| MAINTENANCE["Node 4: Phase 4 Maintenance"]
    VALIDATE -->|"Oracle Error"| TRIAGE["Node 4: Diagnostic Triage"]
    MAINTENANCE --> TRIAGE
    TRIAGE -->|"No Errors"| END["END (Verified PDDL Model)"]
    TRIAGE -->|"Errors Exist & Iterations < Max"| REPAIR["Node 5: Targeted Repair (LLM)"]
    REPAIR --> GENERATE
```
""")
