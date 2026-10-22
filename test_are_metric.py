"""
test_are_metric.py
Demonstration and validation of Action Reconstruction Error (ARE / Structural F1).
Runs Kuhn-Munkres bipartite operator matching over classical STRIPS action models.
"""
from eval.action_reconstruction import evaluate_action_reconstruction

# 1. Reference Domain (Ground Truth Blocksworld)
reference_pddl = """(define (domain blocksworld-reference)
  (:requirements :strips)
  (:predicates (clear ?x) (ontable ?x) (handempty) (holding ?x) (on ?x ?y))

  (:action pickup
    :parameters (?ob)
    :precondition (and (clear ?ob) (ontable ?ob) (handempty))
    :effect (and (holding ?ob) (not (clear ?ob)) (not (ontable ?ob)) (not (handempty))))

  (:action putdown
    :parameters (?ob)
    :precondition (holding ?ob)
    :effect (and (clear ?ob) (handempty) (ontable ?ob) (not (holding ?ob))))

  (:action stack
    :parameters (?ob ?underob)
    :precondition (and (clear ?underob) (holding ?ob))
    :effect (and (handempty) (clear ?ob) (on ?ob ?underob) (not (clear ?underob)) (not (holding ?ob))))

  (:action unstack
    :parameters (?ob ?underob)
    :precondition (and (on ?ob ?underob) (clear ?ob) (handempty))
    :effect (and (holding ?ob) (clear ?underob) (not (on ?ob ?underob)) (not (clear ?ob)) (not (handempty)))))
"""

# 2. Perfect Candidate with Synonyms & Renamed Actions
candidate_perfect_synonyms = """(define (domain blocksworld-agent)
  (:requirements :strips)
  (:predicates (clear ?b) (ontable ?b) (handempty) (holding ?b) (on ?b ?under))

  (:action pick-up
    :parameters (?b)
    :precondition (and (clear ?b) (ontable ?b) (handempty))
    :effect (and (holding ?b) (not (clear ?b)) (not (ontable ?b)) (not (handempty))))

  (:action drop-block
    :parameters (?b)
    :precondition (holding ?b)
    :effect (and (clear ?b) (handempty) (ontable ?b) (not (holding ?b))))

  (:action stack-block
    :parameters (?b ?under)
    :precondition (and (clear ?under) (holding ?b))
    :effect (and (handempty) (clear ?b) (on ?b ?under) (not (clear ?under)) (not (holding ?b))))

  (:action unstack
    :parameters (?b ?under)
    :precondition (and (on ?b ?under) (clear ?b) (handempty))
    :effect (and (holding ?b) (clear ?under) (not (on ?b ?under)) (not (clear ?b)) (not (handempty)))))
"""

# 3. Flawed Candidate (Missing Precondition in stack, Missing Delete Effect in pick-up)
candidate_flawed = """(define (domain blocksworld-flawed)
  (:requirements :strips)
  (:predicates (clear ?b) (ontable ?b) (handempty) (holding ?b) (on ?b ?under))

  (:action pick-up
    :parameters (?b)
    :precondition (and (clear ?b) (ontable ?b) (handempty))
    :effect (and (holding ?b)))  ; BUG: Missing (not (clear ?b)), (not (handempty)), (not (ontable ?b))

  (:action drop-block
    :parameters (?b)
    :precondition (holding ?b)
    :effect (and (clear ?b) (handempty) (ontable ?b) (not (holding ?b))))

  (:action stack-block
    :parameters (?b ?under)
    :precondition (holding ?b)  ; BUG: Missing (clear ?under)
    :effect (and (handempty) (clear ?b) (on ?b ?under) (not (clear ?under)) (not (holding ?b))))

  (:action unstack
    :parameters (?b ?under)
    :precondition (and (on ?b ?under) (clear ?b) (handempty))
    :effect (and (holding ?b) (clear ?under) (not (on ?b ?under)) (not (clear ?b)) (not (handempty)))))
"""

def print_report(title: str, results: dict):
    print(f"\n================================================================================")
    print(f"  {title}")
    print(f"================================================================================")
    print(f"  Macro Structural F1       : {results['macro_structural_f1']:.4f}")
    print(f"  Mean Precondition F1      : {results['mean_precondition_f1']:.4f}")
    print(f"  Mean Add-Effect F1        : {results['mean_add_effect_f1']:.4f}")
    print(f"  Mean Delete-Effect F1     : {results['mean_delete_effect_f1']:.4f}")
    print(f"\n  [Discovered Kuhn-Munkres Action Mapping]")
    for gen_act, ref_act in results['action_mapping'].items():
        print(f"    '{gen_act}'  ===>  '{ref_act}'")
    print(f"\n  {'Generated':<15} {'Matched Reference':<20} {'Pre F1':<8} {'Add F1':<8} {'Del F1':<8} {'Struct F1':<10}")
    print(f"  {'-'*15} {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
    for op in results['detailed_operator_reports']:
        print(f"  {op['generated_action']:<15} {op['ground_truth_action']:<20} {op['precondition_f1']:<8.2f} {op['add_effect_f1']:<8.2f} {op['delete_effect_f1']:<8.2f} {op['structural_f1']:<10.2f}")

if __name__ == "__main__":
    res_perfect = evaluate_action_reconstruction(reference_pddl, candidate_perfect_synonyms)
    print_report("TEST 1: PERFECT ALIGNMENT WITH SYNONYMS (drop-block vs putdown, etc.)", res_perfect)

    res_flawed = evaluate_action_reconstruction(reference_pddl, candidate_flawed)
    print_report("TEST 2: FLAWED DOMAIN (Missing Preconditions & Missing Delete Effects)", res_flawed)
