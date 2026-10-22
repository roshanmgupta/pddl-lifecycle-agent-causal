"""
Centralized Classical PDDL 2.1 (STRIPS + Typing) Standards.

================================================================================
NOTE & MANDATORY AUDIT REQUIREMENT (See AGENTS.md):
Before adding, modifying, or refining ANY rule in this file, you MUST inspect AGENTS.md.
We are building a general-purpose, domain-agnostic agent for PDDL lifecycle engineering.
NEVER add rules, heuristics, or examples tailored to a single specific domain (e.g., barman,
gripper, blocksworld, logistics, satellite). All rules must be universally derived from the formal
specifications of Classical PDDL 2.1 (:strips :typing) and apply to ALL arbitrary planning domains.
Illustrative examples must only use generic, domain-independent archetypes (e.g. entity,
location, vehicle, item, container, receptacle) to illustrate universal syntactic and relational principles.
================================================================================
"""

STANDARD_CLASSICAL_PDDL_RULES = """
STANDARD CLASSICAL PDDL (STRIPS + TYPING) RULES:
1. REQUIREMENTS & SYNTAX:
   - Requirements must strictly be [":strips", ":typing"].
   - All variable names in predicates, parameters, preconditions, and effects must start with '?' (e.g., '?x', '?y').
   - PDDL expressions must be well-formed with balanced parentheses.
   - Naming conventions: Use lowercase, hyphenated names (e.g., 'mobile-unit', 'unit-at-location', 'manipulator-free').

2. TYPES & PREDICATES:
   - Types must form a valid acyclic hierarchy where every declared type inherits from 'object' or a declared parent type. No cycles in hierarchy (a type cannot be its own ancestor). (Ref: NL2PDDL Appendix p. 1)
   - NO DUPLICATE PREDICATE NAMES (PREDICATE OVERLOADING STRICTLY FORBIDDEN): In Classical PDDL, each predicate symbol name MUST appear EXACTLY ONCE in 'predicates'. PDDL engines and validators (VAL, Fast Downward) do NOT support function/predicate overloading by parameter type signature.
     * If the same relation applies across multiple entity types that share a declared common supertype (e.g., both 'vehicle' and 'cargo' inherit from 'physical-item', and both have locations), NEVER declare both '(at ?v - vehicle ?loc - location)' and '(at ?c - cargo ?loc - location)'! You MUST declare '(at ?x - physical-item ?loc - location)' ONCE using the common supertype. In PDDL :typing, declaring a parameter with supertype 'physical-item' automatically permits all of its subtypes.
     * If the relation applies to disjoint types representing distinct operational states or resources (e.g., an agent's manipulator being free vs a storage receptacle being empty), declare two separate, dedicated predicate names (e.g., '(manipulator-free ?m - manipulator)' and '(receptacle-empty ?r - receptacle)'). Never reuse or overload a single predicate symbol across conflicting, disjoint types.
   - NEVER Use Union Types (Strictly Forbidden): Each predicate argument and action parameter MUST have EXACTLY ONE declared type. Never declare union types like '(?x - (type_a | type_b))' or '(?x - (either a b))'. If an attribute applies to multiple disjoint types without a common supertype, create separate dedicated predicates (e.g., '(stored-in ?item - cargo ?rec - receptacle)' and '(mounted-on ?dev - device ?veh - vehicle)'). (Ref: NL2PDDL Appendix p. 4, 7, 22)
   - Argument-Parameter Type Compatibility: When a predicate is used in an action, argument types must inherit from or equal its declared predicate parameter types.
   - PROBLEM OBJECTS VS DOMAIN CONSTANTS (DISJOINTNESS & SCOPE):
     * In Classical PDDL 2.1, all scenario-specific entities listed in problem instance descriptions (e.g. under 'Objects:' or 'Problem:') belong STRICTLY in 'problem.objects'.
     * 'domain.constants' is reserved strictly for universal entities that exist in every conceivable scenario and are referenced directly inside action schema definitions. For standard benchmarks, 'domain.constants' should normally be empty ('{}').
     * NEVER declare problem scenario objects in 'domain.constants'. NEVER declare the same symbol in both domain 'constants' and problem 'objects'—they must be completely disjoint.
   - PREDICATE PREFIX NOTATION IN INITIAL AND GOAL STATES:
     * Every atomic formula in 'problem.initial_state' and 'problem.goal_state' MUST have prefix syntax: '(predicate_symbol arg1 arg2 ...)' where 'predicate_symbol' is an EXACT declared predicate name in 'domain.predicates'.
     * An object name or constant can NEVER be placed in the predicate (first) position!
     * If requirements state a relation between entities (e.g. 'A is the store of B'), declare the relational predicate '(store-of ?s - store ?r - rover)' in 'domain.predicates' and write the fact in prefix form as '(store-of A B)'. Writing '(A store-of B)' is strictly invalid PDDL syntax.
   - UNARY STATE PROPERTY INVARIANT (PROPERTIES VS PHANTOM OBJECTS):
     * When requirements describe an environmental condition, quality, or feature at a location or entity (e.g. "location X is at the sample", "location Y has feature F", "surface S is clean") where the condition has NO separate object in problem ':objects':
     * In First-Order Logic, model this as a UNARY predicate/property over the existing entity/location parameter (e.g. '(at-sample ?loc - location)' or '(has-feature ?loc - location)').
     * NEVER invent undeclared phantom types or dummy objects (e.g. do NOT create a type 'soil-sample' or object 'sample' when problem ':objects' has zero instances).

3. ACTION SCHEMAS:
   - Each action has 'action_name', 'parameters', 'preconditions', and 'effects'.
   - Parameter declarations must specify exactly one type for each variable (e.g., '?x': 'type_name').
   - Scoping: Every variable used in preconditions and effects MUST be declared in the action's 'parameters'. In Classical STRIPS, do NOT use undeclared variables, inline type annotations (e.g., '?x - type_name'), or quantifiers ('exists', 'forall') in preconditions or effects.
   - Preconditions: Conditions that must be true to execute the action.
     * Groundability & Reflexive Variable Invariant: Every precondition literal must be groundable by at least one combination of typed objects from problem ':init' or reachable action effects. Never repeat variables reflexively (e.g., '(at ?x ?x)') when referencing an entity and its station or host; declare a distinct parameter for the location/host (e.g., '?loc - location') and assert '(at ?entity ?loc)'.
     * Spatial/Relational Mediated Binding: If a spatial relation in ':init' (e.g., 'visible', 'connected') is defined between locations, an action requiring interaction or transmission between entities must bind their respective locations and assert the spatial relation between the locations (e.g., '(at ?a ?l1)', '(at ?b ?l2)', '(visible ?l1 ?l2)').
   - Effects & State Transition Completeness: Facts added '(pred ?x)' and facts deleted '(not (pred ?x))'. Always model complete state transitions (e.g., for relocation: delete old location and add new location; for state change: add newly active state '(active ?e)' and delete previous state '(not (idle ?e))'). Every state variable required as a precondition or deleted by an action MUST have an enabling producer action that asserts it. An action must never assert both '(pred ?x)' and '(not (pred ?x))' for the same literal simultaneously. (Ref: NL2PDDL Appendix p. 15, 22)
     * Reversible Operational Resources & Channel Locks: If requirements state that an operational resource or channel is freed/available upon completion (e.g., 'it is the case that channel B is free and A is available') while noting it was occupied during the action, the net post-condition effect MUST assert the positive atoms '(channel-free ?b)' and '(available ?a)' rather than permanently deleting them into an absorbing dead-end state.
     * Classical STRIPS Disjunction Decomposition Rule: In Classical STRIPS (:strips :typing), disjunctive preconditions ('or') are strictly forbidden. When natural language requirements specify multiple restriction clauses or bidirectional movement for a capability (e.g. 'A is above B' vs 'B is above A', or multiple alternative enabling conditions), each distinct restriction MUST be modeled as a SEPARATE, uniquely-named action schema (e.g. appending '_1' and '_2', or '_up' and '_down'). Never omit or collapse alternative conditions into a single action.

4. PROBLEM DEFINITIONS & 3-STAGE REASONING:
   - 'problem.domain_name' must match 'domain.domain_name' exactly.
   - Three-Stage Problem Derivation:
     1. Identify full object inventory and object types/constants needed for the task.
     2. Derive the complete initial state facts (including 0-arity predicates when implied, and explicit locations/states for all physical entities).
     3. Derive the complete goal state facts.
   - Object Declaration Completeness: Every object referenced in 'initial_state' and 'goal_state' MUST be explicitly declared in 'objects' with its single declared type.
   - Cardinality & Completeness: Phrases like "each", "all", "both", "every", or "all destinations" require facts for every mentioned entity, not just one representative. Be conservative: do not omit unary, support, location, holding, availability, or emptiness facts required to make the intended state fully specified.
   - State Predicates vs Object Existence: If the natural language states a resource or container is empty, not available, or free, model that through the relevant state predicates rather than removing typed objects, unless the text explicitly states the objects themselves do not exist.
"""

STANDARD_DIAGNOSTIC_RULES = """
DIAGNOSTIC GUIDELINES:
- Analyze the failure reported by the validator or planner:
  * 'SYNTAX_PARSE': Malformed expressions, unclosed parentheses, or syntax errors.
  * 'TYPE_SIGNATURE': Type mismatch between arguments and the declared predicate signature, arity mismatch, or undeclared constant/object symbols ('Undefined object Got: <name>'). Advise declaring the symbol in domain 'constants' with its type or in problem 'objects'.
    - Check the type hierarchy in domain 'types'! When an object in ':init' or ':goal' triggers 'parameter N is incorrectly typed', check whether the object's type should inherit from the expected parameter type according to the problem requirements (e.g., child type 'subtype_element' should inherit from parent type 'supertype_element'). If so, target domain 'types' and explicitly advise declaring the child type as inheriting from the parent type (e.g., 'subtype_element': 'supertype_element'). Do NOT alter the predicate signature if it already expects the correct parent type!
    - Conversely, if the expected parameter type is ALREADY a declared subtype of the passed argument's type (e.g. predicate was declared expecting specialized 'subtype_element' inheriting from 'supertype_element', but the object has declared type 'supertype_element'): In Classical PDDL (:typing), a supertype cannot be substituted where a subtype is expected. Advise generalizing parameter N of the predicate to 'supertype_element' in domain 'predicates', OR if problem requirements dictate that the object is specifically an instance of 'subtype_element', declare the object as 'subtype_element' in problem ':objects'. NEVER advise declaring 'supertype_element' as a subtype of 'subtype_element' in domain 'types' (subtyping cannot be inverted).
    - Check for DUPLICATE predicate declarations in 'predicates'! If a predicate symbol (e.g. 'at') is declared more than once with conflicting types, VAL binds to the first declaration and rejects the other. Advise eliminating the duplicate declaration and declaring a single unified predicate with the common supertype.
    - Check for PREDICATE ARITY MISMATCH / OVERLOADING ('too few parameters' / 'too many parameters')! In Classical PDDL 2.1, predicate symbols CANNOT be overloaded with multiple arities or conflicting physical concepts. If an action uses '(pred arg)' with arity N, but 'pred' was declared in 'predicates' with arity M != N, the action is using the wrong predicate or attempting to overload 'pred'. Advise declaring a separate, dedicated predicate symbol for the distinct relation (e.g. unary '(at-<feature> ?loc)' vs binary '(at ?entity ?loc)') in domain 'predicates' and using that dedicated symbol in the action schemas.
    - If the passed argument type and the declared predicate parameter type share a common supertype in domain 'types' (e.g. both 'subtype_a' and 'subtype_b' inherit from 'supertype_t'), the predicate was declared too narrowly. Advise GENERALIZING the predicate's parameter declaration to the common supertype in 'predicates' (e.g. '(rel ?arg1 - supertype_t ?arg2 - location)').
    - If the types are disjoint and represent distinct operational states (e.g. manipulator state vs receptacle state), advise declaring distinct, dedicated predicates (e.g. '(manipulator-free ?m - manipulator)' and '(receptacle-empty ?r - receptacle)').
    - NEVER advise an action that manipulates a subtype 'sub_item' to use an ad-hoc predicate restricted to a sister subtype 'sub_other'! Arguments must always inherit from or equal the declared parameter type.
    - Check for UNDECLARED CONSTANTS OR PHANTOM TYPES ('Object with unknown type: <symbol>'):
      * When VAL reports 'Object with unknown type: <symbol>', the symbol was referenced as an object or constant without a type declaration in domain 'constants' or problem 'objects'.
      * If '<symbol>' is used as a constant or literal entity in a domain action schema, note that domain action schemas cannot access problem ':objects'. Either declare its type in domain 'constants' (e.g. '<symbol> - <type>') and remove it from problem ':objects' to prevent duplicate object errors, declare it as an action parameter, or model the condition as a state predicate (e.g. unary property) without referencing an undeclared constant.
      * If '<symbol>' is a parameter type in an action schema and problem ':objects' has zero instances of it, do NOT declare '<symbol>' in domain 'types' (this makes the action ungroundable). Advise removing the phantom parameter from the action and modeling the condition as a state predicate over existing parameters.
    - Check for UNDECLARED PREDICATE OR OBJECT IN PREDICATE POSITION ('Predicate <name> not found'):
      * When VAL reports 'Predicate <name> not found' during initial state or goal checking:
      * If '<name>' is declared in problem 'objects' or domain 'constants', an object name was erroneously placed in the first (predicate) position of an atom! (e.g. '(obj1 relation obj2)').
        Advise: "In Classical PDDL, every fact must use prefix notation '(predicate_symbol arg1 arg2 ...)'. Object '<name>' cannot be in the predicate position. Declare the intended relational predicate in domain 'predicates' (e.g. '(rel ?x - type1 ?y - type2)') and format the atom as '(rel obj1 obj2)' in problem 'initial_state'."
      * If '<name>' is not in 'objects' or 'constants', the domain's 'predicates' is missing the declaration.
        Advise: "Declare predicate '(<name> ...)' in domain 'predicates' with its typed parameter signature matching its arguments in problem 'initial_state' / 'goal_state', or if the atom used a misspelled predicate name, update the atom to use the correct declared predicate."
  * 'GROUNDING_UNSOLVABILITY': Planner reports no plan found, unachievable goals, or empty reachable operators.
    - Check for EMPTY ACTION PARAMETER DOMAINS (0 Groundings Action Lockout):
      * In Classical PDDL 2.1 (:typing), every parameter '?p - T' in an action schema requires that at least one object in problem ':objects' or domain ':constants' has type 'T' (or inherits from 'T').
      * If problem ':objects' contains zero objects of type 'T' (or its subtypes), the action has 0 groundings and can NEVER be instantiated or executed!
      * Advise: In problem ':objects', declare the relevant objects as type 'T' according to the natural language requirements (e.g. if the requirements designate certain entities as that specialized type), or if the action was intended to accept the broader supertype, generalize parameter '?p' to that supertype in domain 'actions'.
    - NEVER advise relaxing or deleting preconditions that are explicitly specified in the Natural Language Requirements (e.g. if the text explicitly states 'I can only lift if the item is clear and on the surface', NEVER suggest removing '(clear ?item)' or '(on ?item ?surface)'). Conditions mandated by requirements are physically essential.
    - Check for MISSING TRANSITION / CLEARING EFFECTS: When an action removes an entity from a support surface, receptacle, or container, check if the action omitted a positive state-clearing effect explicitly described in the requirements (e.g., 'C is clear' -> '(clear ?s)'; 'container is empty' -> '(empty ?c)'). Omitting state-clearing effects on vacated supports makes underlying items permanently unreachble.
    - Verify that all positive effects described in the requirements are included in the action's effects.
  * 'HISTORICAL_REGRESSION': Failure of a historical test case. When a historical test case fails with 'Predicate <name> not found' or 'Type <name> not found', target the domain's 'predicates' or 'types'. Explicitly advise adding the missing predicate signature or missing types to the domain blueprint to restore backward compatibility.
- Authoritative Diagnostics & Grounded Evidence:
  * Automatic parser, domain, planner, and validator diagnostics are authoritative for formal compatibility.
  * Base every diagnostic report on explicit evidence from the natural language description, current PDDL blueprints, or oracle diagnostic logs. Do not speculate about unstated requirements.
- Anti-Oscillation & Stable Diagnostic Guidance:
  * Do not alternate between "this fact should be present" and "this fact should be removed" across iterations. Prefer stable, minimal repair guidance.
  * PRESCRIPTIVE REPAIR DIRECTIVES (NO VAGUE SYMPTOM RESTATEMENTS): Hints must be strictly prescriptive rather than descriptive. Never merely restate what happened or paraphrase raw logs. Always specify: 1) exact AST target component, 2) concrete repair operation, 3) the exact PDDL literal or signature to add, modify, or invert.
"""

STANDARD_REPAIR_RULES = """
REPAIR INSTRUCTIONS:
- MINIMAL EDITS & DRAFT PRESERVATION:
  * Treat the current blueprints as a draft to edit, not disposable context.
  * Preserve all parts of the current draft that are already correct. Apply the smallest set of surgical changes needed to satisfy feedback.
  * If the 'objects' section is already correct, keep it unchanged. Prefer minimal edits over full rewrites of ':init' and ':goal' facts.
- PRESERVE ALL ACTIONS: Output action count MUST equal or exceed the baseline input count. NEVER remove, drop, or omit valid existing actions to bypass a verification error; repair the action's preconditions or effects instead. (Ref: NL2PDDL Appendix p. 15)
- For HISTORICAL_REGRESSION / BACKWARD COMPATIBILITY:
  * When a historical problem fails validation with 'Predicate <name> not found' or 'Type <name> not found', you MUST add the missing predicate or type signature to the domain blueprint's 'predicates' or 'types'! Domains must declare all legacy predicates used by historical test cases to remain backward compatible.
  * If legacy problems use previous action mechanics, ensure that new preconditions (e.g. maintenance checks) do not prevent legacy plans from executing unless restorative actions are reachable.
- Ensure all variables used in preconditions and effects are declared in action parameters. Never use undeclared variables or inline types (like '?x - type') inside precondition or effect literals.
- For type errors: If an object in ':init' or ':goal' triggers a parameter type error, check domain 'types' first! If the object's declared type is conceptually a subtype of the expected parameter type (e.g., child type 'subtype_element' should inherit from parent type 'supertype_element'), update domain 'types' to declare the inheritance (e.g., 'subtype_element': 'supertype_element'). Do NOT alter the predicate signature if it already expects the correct parent type!
  * Conversely, if the expected parameter type is ALREADY a declared subtype of the object's declared type (e.g. predicate expects 'subtype_element' which inherits from 'supertype_element', but the object in problem ':objects' has type 'supertype_element'): In Classical PDDL, a supertype cannot be passed to a parameter expecting a subtype. Generalize the predicate's parameter declaration to 'supertype_element' in domain 'predicates', OR if problem requirements state that the object is specifically an instance of 'subtype_element', declare the object as 'subtype_element' in problem ':objects'. NEVER declare 'supertype_element' as a subtype of 'subtype_element' in domain 'types' (subtyping cannot be inverted).
  * If a predicate name appears multiple times with conflicting types, remove the duplicate and keep only the unified declaration with the common supertype (e.g., '(at ?x - physical-item ?l - location)').
  * If an argument type and a declared parameter type share a common supertype (e.g. 'subtype_a' and 'subtype_b' both inherit from 'supertype_t'), generalize the predicate declaration to the common supertype in 'predicates' (e.g., '(contains ?c - container ?s - substance)').
  * If the entities are of disjoint types with different meanings (e.g. manipulator status vs receptacle status), use separate, distinct predicate names (e.g. '(manipulator-free ?m - manipulator)' and '(receptacle-empty ?r - receptacle)'). Never introduce narrow ad-hoc predicates tailored to an unrelated subtype.
- ANTI-OSCILLATION FOR PREDICATE SIGNATURES: Predicate parameter types are strictly invariant across the entire domain. If one action uses a predicate with type A and another action uses it with type B, check if A and B share a supertype T; if so, declare the parameter as type T. If they are disjoint, declare two separate, distinct predicate names. DO NOT alternate the predicate's declared parameter type back and forth across repair iterations.
- NO CONFLICTING SIMULTANEOUS EFFECTS: Never produce an action effect that asserts and deletes the exact same literal simultaneously (e.g., '(and (pred ?x) (not (pred ?x)))'). If an action appears to require this, the action is conflating two distinct physical states that require two separate predicate declarations.
- FAITHFULNESS TO DOMAIN CONTRACTS: Never introduce predicates, object types, constants, or syntax that are unsupported by the domain definition.
- Ensure predicate usage matches declared parameter types.
- Ensure all variable names start with '?'.
- For 'Predicate <name> not found' / Object in predicate position:
  * In Classical PDDL 2.1 prefix notation, every fact in problem ':init' and ':goal' MUST begin with a declared predicate symbol from 'domain.predicates'. An object name can NEVER be in the predicate position.
  * If problem ':init' contains an atom where an object is placed first (e.g. '(object1 rel-name object2)'), declare the relational predicate '(rel-name ?x - type1 ?y - type2)' in domain 'predicates' and update the atom in problem 'initial_state' to prefix form '(rel-name object1 object2)'.
  * Move all scenario-specific objects from 'domain.constants' to 'problem.objects'. Keep 'domain.constants' as '{}' unless universal constants are explicitly needed.
- If an oracle reports an undefined object (e.g., 'Undefined object Got: <name>'), declare the symbol in domain 'constants' with its declared type, or add it to problem 'objects'. NEVER declare the same symbol in both domain 'constants' and problem 'objects'—they must be completely disjoint.
- DEAD UNGROUNDABLE PRECONDITIONS & SOLVABILITY:
  * EMPTY ACTION PARAMETER DOMAIN (0 Groundings Action Lockout): When reachability analysis flags that an action parameter '?p - T' has ZERO matching objects in problem ':objects' or domain ':constants':
    In Classical PDDL 2.1, that action has 0 possible groundings and can never execute. To repair: Check the natural language requirements. If the scenario designates specific objects as instances of type 'T' (e.g. entities that serve as specialized subtypes), update problem ':objects' to declare them as type 'T'. Alternatively, if the action was intended to accept the broader supertype, generalize parameter '?p' to that supertype in domain 'actions'.
  * STRICT FORBIDDEN ACTION: NEVER relax, remove, or delete a precondition that is explicitly stipulated in the Natural Language Requirements (e.g. requiring an item to be clear, on a surface, in a container, or an agent being available/at a location). Conditions demanded by requirements are physically essential.
  * When the planner cannot find a plan ('GROUNDING_UNSOLVABILITY'), audit the action ':effects' against the requirements text: restore any omitted positive effects explicitly stated in the text (such as clearing a surface/container when an item is removed, asserting availability, restoring capacity, or asserting a goal relation like an item being on a surface or in a receptacle when dropped/placed/loaded).
  * ORPHANED GOAL PREDICATES: If a goal predicate has NO action in the domain producing it, check the requirements for the action that establishes that relationship (e.g. dropping, placing, loading, or assembling) and add the missing positive effect literal. NEVER remove legitimate delete effects from actions that remove/lift the object!
  * When reachability analysis or planner flags dead ungroundable preconditions (e.g. static relation with zero matches in ':init' or reflexive variable equality '(at ?x ?x)'):
  * Check whether the action checked a spatial/topological relation directly against an agent/device rather than its location. Introduce the missing location parameter (e.g. '?loc - location'), bind the entity to the location '(at ?agent ?loc)', and assert the spatial relation between locations (e.g. '(visible ?loc1 ?loc2)').
  * When causal analysis flags 'Variable conflation on parameter ?x': Static preconditions share parameter ?x, but their valid objects in problem ':init' are completely disjoint. In Classical PDDL, static relations cannot change during execution, so verify parameter bindings against the requirements to ensure parameter '?x' is not conflating two distinct physical entities or roles.
  * DIRECTIONAL ASYMMETRY & MISSING INVERSE ACTIONS: When diagnostic analysis reports that a transition action moves entities along an asymmetric static relation R(?from, ?to), but goals require movement in the reverse direction where R(?dest, ?start) holds:
    In Classical STRIPS (:strips :typing), disjunction ('or') in preconditions is strictly unsupported. Add the missing reverse action schema (e.g. '<action_name>_reverse' or '<action_name>_up') with precondition 'R(?to, ?from)' and matching transition effects described in the requirements.
- NO NEGATIVE PRECONDITIONS IN STRIPS: Never introduce negative literals like '(not (...))' in action ':precondition' unless ':negative-preconditions' is explicitly declared in domain ':requirements'. Classical STRIPS domains forbid negative preconditions. Model absent conditions using positive complement predicates (e.g. '(empty ?s)' or '(available ?a)').
- NO ARTIFICIAL RESTORATION ACTIONS: Never create artificial standalone actions (e.g. 'restore_available') to reverse deleted states. If an action temporarily claims and releases an operational resource or agent state (such as channel locks or availability), ensure that action directly asserts the positive atom in its ':effect' upon completion, or omit the delete effect under STRIPS add-after-delete.
- Ensure problem.domain_name matches domain.domain_name exactly.
"""
