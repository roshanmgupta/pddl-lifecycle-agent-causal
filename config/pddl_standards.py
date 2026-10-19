"""
Centralized Classical PDDL 2.1 (STRIPS + Typing) Standards.
Strictly limited to the standard rules of Classical PDDL (:strips :typing).
No additional experimental or domain-specific rules.
"""

STANDARD_CLASSICAL_PDDL_RULES = """
STANDARD CLASSICAL PDDL (STRIPS + TYPING) RULES:
1. REQUIREMENTS & SYNTAX:
   - Requirements must strictly be [":strips", ":typing"].
   - All variable names in predicates, parameters, preconditions, and effects must start with '?' (e.g., '?x', '?y').
   - PDDL expressions must be well-formed with balanced parentheses.
   - Naming conventions: Use lowercase, hyphenated names (e.g., 'delivery-robot', 'robot-at-location', 'hand-empty').

2. TYPES & PREDICATES:
   - Types must form a valid hierarchy where every declared type inherits from 'object' or a declared parent. No cycles in hierarchy (a type cannot be its own ancestor). (Ref: NL2PDDL Appendix p. 1)
   - Unique Predicate Declarations: In PDDL, each predicate symbol must be declared exactly once. Declaring the same predicate name multiple times with different types is illegal (no overloading).
   - NEVER Use Union Types (Strictly Forbidden): Each predicate argument and action parameter MUST have EXACTLY ONE type. Never declare union types like '(?x - (block | table))' or '(?x - (either a b))'. If an attribute applies to multiple types, either define a common supertype or create separate predicates (e.g., '(on-table ?b - block)' and '(on-block ?b1 - block ?b2 - block)'). (Ref: NL2PDDL Appendix p. 4, 7, 22)
   - When a predicate is used in an action, argument types must match its declared parameter types.
   - DOMAIN CONSTANTS & OBJECTS DISJOINTNESS: In classical PDDL 2.1, fixed domain-wide objects referenced directly in action preconditions or effects can be declared in the domain 'constants' dictionary mapping constant name to its type (e.g., {'c1': 'type_name'}). Domain constants are global to all problems. Therefore, NEVER declare the same symbol in both domain 'constants' and problem 'objects'—they must be completely disjoint.

3. ACTION SCHEMAS:
   - Each action has 'action_name', 'parameters', 'preconditions', and 'effects'.
   - Parameter declarations must specify exactly one type for each variable (e.g., '?x': 'type_name').
   - Scoping: Every variable used in preconditions and effects MUST be declared in the action's 'parameters'. In Classical STRIPS, do NOT use undeclared variables, inline type annotations (e.g., '?h - hoist'), or quantifiers ('exists', 'forall') in preconditions or effects.
   - Preconditions: Conditions that must be true to execute the action.
   - Effects & State Transition Completeness: Facts added '(pred ?x)' and facts deleted '(not (pred ?x))'. Always model complete state transitions (e.g., for movement: delete old location and add new location; for pickup: add holding and delete hand-empty). An action must not assert both '(pred ?x)' and '(not (pred ?x))' for the same literal simultaneously. (Ref: NL2PDDL Appendix p. 15, 22)

4. PROBLEM DEFINITIONS:
   - 'problem.domain_name' must match 'domain.domain_name' exactly.
   - All objects referenced in 'initial_state' and 'goal_state' must be declared in 'objects' with their types.
   - 'initial_state' contains the ground facts that are true initially. For all physical entities that require locations to be manipulated (e.g., crates, pallets, packages, vehicles), their initial locations must be explicitly stated in 'initial_state'.
   - 'goal_state' contains the target facts to achieve.
"""

STANDARD_DIAGNOSTIC_RULES = """
DIAGNOSTIC GUIDELINES:
- Analyze the failure reported by the validator or planner:
  * 'SYNTAX_PARSE': Malformed expressions, unclosed parentheses, or syntax errors.
  * 'TYPE_SIGNATURE': Type mismatch between arguments and the declared predicate signature, arity mismatch, or undeclared constant/object symbols ('Undefined object Got: <name>'). Advise declaring the symbol in domain 'constants' with its type or in problem 'objects'.
    Note: If the failing predicate is declared multiple times in 'predicates' with different types (e.g., '(at ?h - hoist ...)' and '(at ?t - truck ...)'), VAL ignores the subsequent declarations! You MUST advise merging them into a SINGLE predicate declaration using a common supertype in 'types' or renaming to distinct predicates.
  * 'GROUNDING_UNSOLVABILITY': Planner reports no plan found, unachievable goals, or empty reachable operators.
  * 'HISTORICAL_REGRESSION': Failure of a historical test case. When a historical test case fails with 'Predicate <name> not found' or 'Type <name> not found', target the domain's 'predicates' or 'types'. Explicitly advise adding the missing predicate signature (e.g., '(at_passenger ?p - passenger ?c - city)') or missing types to the domain blueprint to restore backward compatibility.
- Identify the faulty AST element (action name, predicate, or object).
- Suggest a targeted repair operation to resolve the error according to standard PDDL.
"""

STANDARD_REPAIR_RULES = """
REPAIR INSTRUCTIONS:
- PRESERVE ALL ACTIONS: Output action count MUST equal or exceed the baseline input count. NEVER remove, drop, or omit valid existing actions to bypass a verification error; repair the action's preconditions or effects instead. (Ref: NL2PDDL Appendix p. 15)
- For HISTORICAL_REGRESSION / BACKWARD COMPATIBILITY:
  * When a historical problem fails validation with 'Predicate <name> not found' or 'Type <name> not found', you MUST add the missing predicate or type signature to the domain blueprint's 'predicates' or 'types'! Domains must declare all legacy predicates used by historical test cases to remain backward compatible.
  * If legacy problems use previous action mechanics, ensure that new preconditions (e.g. maintenance checks) do not prevent legacy plans from executing unless restorative actions are reachable.
- Ensure all variables used in preconditions and effects are declared in action parameters. Never use undeclared variables or inline types (like '?x - type') inside precondition or effect literals.
- For type errors: Check 'predicates' for duplicate predicate names. In PDDL, each predicate name must be declared ONLY ONCE. Merge multiple declarations into a single predicate with a common supertype in 'types' (e.g., '(at ?x - locatable ?d - place)') or use distinct predicate names. Never use union types like '(?x - (a | b))'. (Ref: NL2PDDL Appendix p. 4, 7)
- Ensure predicate usage matches declared parameter types.
- Ensure all variable names start with '?'.
- If an oracle reports an undefined object (e.g., 'Undefined object Got: <name>'), declare the symbol in domain 'constants' with its declared type, or add it to problem 'objects'. NEVER declare the same symbol in both domain 'constants' and problem 'objects'—they must be completely disjoint.
- Ensure problem.domain_name matches domain.domain_name exactly.
"""
