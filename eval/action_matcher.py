import re
import difflib
from typing import Dict, List, Set, Tuple, Any

# Map to treat common synonyms as equivalent in PDDL predicates
SYNONYM_MAP = {
    "pointing": "pointing",
    "pointing_at": "pointing",
    "has_image": "have_image",
    "have_image": "have_image",
    "power_available": "power_avail",
    "power_avail": "power_avail",
    "handempty": "handempty",
    "hand_empty": "handempty",
    "arm_empty": "handempty",
    "clear": "clear",
    "ontable": "ontable",
    "on_table": "ontable",
    "holding": "holding",
    "at": "at",
    "in": "in",
    "inside": "in",
}

def normalize_predicate_name(pred: str) -> str:
    """Normalizes predicate names (lowercase, underscores, synonyms)."""
    clean = pred.strip().lower().replace("-", "_")
    return SYNONYM_MAP.get(clean, clean)

def normalize_predicates(section: str) -> List[str]:
    """Extracts and normalizes all predicates in a precondition or effect section."""
    if not section:
        return []
    preds = re.findall(r"\(?(not\s+)?\(?([a-zA-Z0-9_-]+)", section)
    normalized = []
    for neg, pred in preds:
        base = normalize_predicate_name(pred)
        if base in ["and", "or", "not", "when", "forall", "exists"]:
            continue
        if neg.strip():
            normalized.append(f"not_{base}")
        else:
            normalized.append(base)
    return list(set(normalized))

def extract_actions(pddl_text: str) -> List[Dict[str, Any]]:
    """
    Parses a PDDL domain string and extracts action names, preconditions, and effects.
    """
    actions = []
    # Match actions robustly
    action_matches = re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", pddl_text, re.DOTALL)
    for match in action_matches:
        name = match.group(1).strip()
        body = match.group(2)
        
        pre_match = re.search(r":precondition\s*(.*?)(?=:effect|\)\s*$)", body, re.DOTALL)
        eff_match = re.search(r":effect\s*(.*?)(?=\)\s*$)", body, re.DOTALL)
        
        preconds = normalize_predicates(pre_match.group(1)) if pre_match else []
        effects = normalize_predicates(eff_match.group(1)) if eff_match else []
        
        actions.append({
            "name": name,
            "pre": preconds,
            "eff": effects
        })
    return actions

def jaccard_similarity(set1: List[str], set2: List[str]) -> float:
    """Computes Jaccard set similarity between two lists of normalized predicates."""
    s1, s2 = set(set1), set(set2)
    if not s1 and not s2:
        return 1.0
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union != 0 else 0.0

def action_similarity(a1: Dict[str, Any], a2: Dict[str, Any]) -> float:
    """
    Computes weighted similarity score between two actions based on:
    - Name similarity: 30%
    - Precondition logic overlap: 35%
    - Effect logic overlap: 35%
    """
    n1 = a1["name"].lower().replace("-", "_")
    n2 = a2["name"].lower().replace("-", "_")
    name_score = difflib.SequenceMatcher(None, n1, n2).ratio()
    pre_score = jaccard_similarity(a1["pre"], a2["pre"])
    eff_score = jaccard_similarity(a1["eff"], a2["eff"])
    
    return round(0.30 * name_score + 0.35 * pre_score + 0.35 * eff_score, 4)

def evaluate_action_similarity(gt_pddl: str, generated_pddl: str) -> Dict[str, Any]:
    """
    Evaluates generated domain against ground truth domain using Logic-Aware Action Matching.
    Returns quantitative metrics: precision, recall, F1, average match score, and individual alignments.
    """
    gt_actions = extract_actions(gt_pddl)
    gen_actions = extract_actions(generated_pddl)
    
    matched_scores = []
    matched_pairs = []
    matched_gen_indices = set()
    
    for gt_act in gt_actions:
        best_score = 0.0
        best_idx = -1
        for i, gen_act in enumerate(gen_actions):
            if i in matched_gen_indices:
                continue
            score = action_similarity(gt_act, gen_act)
            if score > best_score:
                best_score = score
                best_idx = i
                
        if best_idx != -1 and best_score >= 0.40:  # Threshold for meaningful alignment
            matched_scores.append(best_score)
            matched_gen_indices.add(best_idx)
            matched_pairs.append({
                "ground_truth_action": gt_act["name"],
                "generated_action": gen_actions[best_idx]["name"],
                "similarity_score": best_score,
                "preconditions_match": jaccard_similarity(gt_act["pre"], gen_actions[best_idx]["pre"]),
                "effects_match": jaccard_similarity(gt_act["eff"], gen_actions[best_idx]["eff"])
            })
            
    gt_count = len(gt_actions)
    gen_count = len(gen_actions)
    matched_count = len(matched_scores)
    
    avg_score = round(sum(matched_scores) / gt_count, 4) if gt_count > 0 else 0.0
    precision = round(matched_count / gen_count, 4) if gen_count > 0 else 0.0
    recall = round(matched_count / gt_count, 4) if gt_count > 0 else 0.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
    
    if avg_score >= 0.85:
        verdict = "EXCELLENT_MATCH"
    elif avg_score >= 0.70:
        verdict = "ACCEPTABLE_MATCH"
    else:
        verdict = "PARTIAL_OR_LOW_MATCH"
        
    return {
        "gt_action_count": gt_count,
        "generated_action_count": gen_count,
        "matched_action_count": matched_count,
        "average_logic_match": avg_score,
        "action_precision": precision,
        "action_recall": recall,
        "action_f1": f1,
        "verdict": verdict,
        "detailed_matches": matched_pairs
    }
