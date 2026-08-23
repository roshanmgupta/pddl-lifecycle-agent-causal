from typing import List
from benchmark.schema import BenchmarkTask, LifecycleTaskType

BENCHMARK_TASKS: List[BenchmarkTask] = [

    # =========================================================================
    # 1. BLOCKSWORLD DOMAIN FAMILY
    # =========================================================================

    # 1.1 Elicitation Task
    BenchmarkTask(
        task_id="blocksworld_elicitation_01",
        domain_family="blocksworld",
        task_type=LifecycleTaskType.ELICITATION,
        title="Blocksworld Domain & Problem Elicitation",
        natural_language_requirements="""
        We need a classical Blocksworld domain.
        There are blocks. A robot arm can pick up a block from the table if the block is clear and the hand is empty.
        The arm can put down a held block onto the table.
        The arm can stack a held block onto another clear block.
        The arm can unstack a clear block from another block if the hand is empty.
        Define a scenario with blocks A, B, and C where block A is on block B, block B is on table, block C is on table, and arm is empty.
        The goal is to have block C on block B, and block B on block A.
        """,
        ground_truth_domain_pddl="""(define (domain blocksworld)
  (:requirements :strips :typing)
  (:types block - object)
  (:predicates
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)
    (handempty)
    (holding ?x - block)
  )

  (:action pick-up
    :parameters (?x - block)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))
  )

  (:action put-down
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x))
  )

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y))
  )

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (on ?x ?y) (clear ?x) (handempty))
    :effect (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y)))
  )
)""",
        ground_truth_problem_pddl="""(define (problem blocksworld_prob_01)
  (:domain blocksworld)
  (:objects a b c - block)
  (:init
    (on a b)
    (ontable b)
    (ontable c)
    (clear a)
    (clear c)
    (handempty)
  )
  (:goal (and (on c b) (on b a)))
)"""
    ),

    # 1.2 Synthetic Fault Repair Task (Missing Precondition)
    BenchmarkTask(
        task_id="blocksworld_repair_missing_precondition_01",
        domain_family="blocksworld",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="Blocksworld Repair: Missing (handempty) Precondition in pick-up",
        fault_category="GROUNDING_UNSOLVABILITY",
        natural_language_requirements="Blocks domain where picking up requires arm to be empty.",
        initial_domain_pddl="""(define (domain blocksworld)
  (:requirements :strips :typing)
  (:types block - object)
  (:predicates
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)
    (handempty)
    (holding ?x - block)
  )

  (:action pick-up
    :parameters (?x - block)
    :precondition (and (clear ?x) (ontable ?x))  ;; FAULT: Missing (handempty)!
    :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))
  )

  (:action put-down
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x))
  )
)""",
        initial_problem_pddl="""(define (problem blocksworld_prob_01)
  (:domain blocksworld)
  (:objects a b - block)
  (:init
    (ontable a)
    (ontable b)
    (clear a)
    (clear b)
    (handempty)
  )
  (:goal (and (holding a) (holding b)))  ;; Unsolvable concurrently without handempty check!
)""",
        ground_truth_domain_pddl="""(define (domain blocksworld)
  (:requirements :strips :typing)
  (:types block - object)
  (:predicates
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)
    (handempty)
    (holding ?x - block)
  )

  (:action pick-up
    :parameters (?x - block)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))
  )

  (:action put-down
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x))
  )
)""",
        ground_truth_problem_pddl="""(define (problem blocksworld_prob_01)
  (:domain blocksworld)
  (:objects a b - block)
  (:init
    (ontable a)
    (ontable b)
    (clear a)
    (clear b)
    (handempty)
  )
  (:goal (and (holding a)))
)"""
    ),

    # =========================================================================
    # 2. LOGISTICS DOMAIN FAMILY
    # =========================================================================

    # 2.1 Elicitation Task
    BenchmarkTask(
        task_id="logistics_elicitation_01",
        domain_family="logistics",
        task_type=LifecycleTaskType.ELICITATION,
        title="Logistics Domain & Problem Elicitation",
        natural_language_requirements="""
        We need a logistics domain with packages, trucks, airplanes, locations, and airports.
        Trucks move between locations in the same city.
        Airplanes fly between airport locations in different cities.
        Packages can be loaded into trucks at locations, and unloaded at locations.
        Packages can be loaded into airplanes at airports, and unloaded at airports.
        Define scenario with truck t1, airplane p1, package pkg1, location loc1, airport apt1 in city1, and airport apt2 in city2.
        pkg1 starts at loc1. Goal is pkg1 at apt2.
        """,
        ground_truth_domain_pddl="""(define (domain logistics)
  (:requirements :strips :typing)
  (:types
    package vehicle location city - object
    truck airplane - vehicle
    airport - location
  )
  (:predicates
    (at ?obj - object ?loc - location)
    (in ?pkg - package ?veh - vehicle)
    (in-city ?loc - location ?c - city)
  )

  (:action drive-truck
    :parameters (?t - truck ?from - location ?to - location ?c - city)
    :precondition (and (at ?t ?from) (in-city ?from ?c) (in-city ?to ?c))
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action fly-airplane
    :parameters (?p - airplane ?from - airport ?to - airport)
    :precondition (at ?p ?from)
    :effect (and (not (at ?p ?from)) (at ?p ?to))
  )

  (:action load-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (at ?pkg ?loc) (at ?t ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?t))
  )

  (:action unload-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (in ?pkg ?t) (at ?t ?loc))
    :effect (and (not (in ?pkg ?t)) (at ?pkg ?loc))
  )
)""",
        ground_truth_problem_pddl="""(define (problem logistics_prob_01)
  (:domain logistics)
  (:objects
    pkg1 - package
    t1 - truck
    p1 - airplane
    loc1 - location
    apt1 apt2 - airport
    city1 city2 - city
  )
  (:init
    (at pkg1 loc1)
    (at t1 loc1)
    (at p1 apt1)
    (in-city loc1 city1)
    (in-city apt1 city1)
    (in-city apt2 city2)
  )
  (:goal (at pkg1 apt2))
)"""
    ),

    # 2.2 Synthetic Fault Repair Task (Type Signature Error)
    BenchmarkTask(
        task_id="logistics_repair_type_mismatch_01",
        domain_family="logistics",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="Logistics Repair: Type Mismatch in load-truck",
        fault_category="TYPE_SIGNATURE",
        natural_language_requirements="Logistics package loading requires package and truck parameter types to match vehicle declarations.",
        initial_domain_pddl="""(define (domain logistics)
  (:requirements :strips :typing)
  (:types
    package vehicle location city - object
    truck airplane - vehicle
    airport - location
  )
  (:predicates
    (at ?obj - object ?loc - location)
    (in ?pkg - package ?veh - vehicle)
  )

  (:action load-truck
    :parameters (?pkg - package ?t - location ?loc - location)  ;; FAULT: ?t typed as location instead of truck!
    :precondition (and (at ?pkg ?loc) (at ?t ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?t))
  )
)""",
        initial_problem_pddl="""(define (problem logistics_prob_01)
  (:domain logistics)
  (:objects pkg1 - package t1 - truck loc1 - location)
  (:init (at pkg1 loc1) (at t1 loc1))
  (:goal (in pkg1 t1))
)""",
        ground_truth_domain_pddl="""(define (domain logistics)
  (:requirements :strips :typing)
  (:types
    package vehicle location city - object
    truck airplane - vehicle
    airport - location
  )
  (:predicates
    (at ?obj - object ?loc - location)
    (in ?pkg - package ?veh - vehicle)
  )

  (:action load-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (at ?pkg ?loc) (at ?t ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?t))
  )
)""",
        ground_truth_problem_pddl="""(define (problem logistics_prob_01)
  (:domain logistics)
  (:objects pkg1 - package t1 - truck loc1 - location)
  (:init (at pkg1 loc1) (at t1 loc1))
  (:goal (in pkg1 t1))
)"""
    ),

    # =========================================================================
    # 3. ROVERS DOMAIN FAMILY
    # =========================================================================

    # 3.1 Elicitation Task
    BenchmarkTask(
        task_id="rovers_elicitation_01",
        domain_family="rovers",
        task_type=LifecycleTaskType.ELICITATION,
        title="Rovers Planetary Exploration Domain",
        natural_language_requirements="""
        Planetary Rover domain. Rovers move between waypoints.
        Rovers sample soil and rock at waypoints.
        Rovers communicate data back to lander at a waypoint.
        Define scenario with rover r1, waypoints w1 and w2, lander l1 at w2.
        r1 starts at w1, samples soil at w1, moves to w2, and communicates soil data to l1.
        """,
        ground_truth_domain_pddl="""(define (domain rovers)
  (:requirements :strips :typing)
  (:types rover waypoint lander store - object)
  (:predicates
    (at ?r - rover ?w - waypoint)
    (at-lander ?l - lander ?w - waypoint)
    (can-traverse ?r - rover ?w1 - waypoint ?w2 - waypoint)
    (equipped-for-soil-analysis ?r - rover)
    (have-soil-data ?w - waypoint)
    (communicated-soil-data ?w - waypoint)
    (empty ?s - store)
    (full ?s - store)
    (store-of ?s - store ?r - rover)
    (at-soil-sample ?w - waypoint)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (at ?r ?from) (can-traverse ?r ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample-soil
    :parameters (?r - rover ?s - store ?w - waypoint)
    :precondition (and (at ?r ?w) (at-soil-sample ?w) (equipped-for-soil-analysis ?r) (store-of ?s ?r) (empty ?s))
    :effect (and (not (empty ?s)) (full ?s) (have-soil-data ?w) (not (at-soil-sample ?w)))
  )

  (:action communicate-soil-data
    :parameters (?r - rover ?l - lander ?w - waypoint ?l-w - waypoint)
    :precondition (and (at ?r ?w) (at-lander ?l ?l-w) (have-soil-data ?w))
    :effect (communicated-soil-data ?w)
  )
)""",
        ground_truth_problem_pddl="""(define (problem rover_prob_01)
  (:domain rovers)
  (:objects
    r1 - rover
    w1 w2 - waypoint
    l1 - lander
    s1 - store
  )
  (:init
    (at r1 w1)
    (at-lander l1 w2)
    (can-traverse r1 w1 w2)
    (can-traverse r1 w2 w1)
    (equipped-for-soil-analysis r1)
    (store-of s1 r1)
    (empty s1)
    (at-soil-sample w1)
  )
  (:goal (communicated-soil-data w1))
)"""
    ),

    # =========================================================================
    # 4. DEPOTS DOMAIN FAMILY
    # =========================================================================

    # 4.1 Elicitation Task
    BenchmarkTask(
        task_id="depots_elicitation_01",
        domain_family="depots",
        task_type=LifecycleTaskType.ELICITATION,
        title="Depots Logistics & Stacking Domain",
        natural_language_requirements="""
        Depots domain combining logistics and block stacking.
        Trucks carry crates between depots.
        Hoists lift crates from trucks or pallets and stack them onto crates or pallets.
        Define scenario with truck t1, hoist h1 at depot d1, crate c1 on pallet p1 at d1.
        Goal is crate c1 loaded in truck t1.
        """,
        ground_truth_domain_pddl="""(define (domain depots)
  (:requirements :strips :typing)
  (:types place locatable - object
         depot - place
         truck hoist surface - locatable
         pallet crate - surface)
  (:predicates
    (at ?x - locatable ?p - place)
    (on ?x - crate ?y - surface)
    (clear ?x - surface)
    (in ?c - crate ?t - truck)
    (lifting ?h - hoist ?c - crate)
    (available ?h - hoist)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (available ?h) (at ?c ?p) (on ?c ?s) (clear ?c))
    :effect (and (not (at ?c ?p)) (not (available ?h)) (not (on ?c ?s)) (not (clear ?c)) (clear ?s) (lifting ?h ?c))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (lifting ?h ?c))
    :effect (and (not (lifting ?h ?c)) (available ?h) (in ?c ?t))
  )
)""",
        ground_truth_problem_pddl="""(define (problem depots_prob_01)
  (:domain depots)
  (:objects
    d1 - depot
    t1 - truck
    h1 - hoist
    p1 - pallet
    c1 - crate
  )
  (:init
    (at t1 d1)
    (at h1 d1)
    (at p1 d1)
    (at c1 d1)
    (on c1 p1)
    (clear c1)
    (available h1)
  )
  (:goal (in c1 t1))
)"""
    ),

    # =========================================================================
    # 5. SATELLITE DOMAIN FAMILY
    # =========================================================================

    # 5.1 Elicitation & Domain Evolution Task
    BenchmarkTask(
        task_id="satellite_evolution_01",
        domain_family="satellite",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="Satellite Domain Evolution: Adding Infrared Imaging Mode",
        natural_language_requirements="""
        Extend existing Satellite domain to support dual imaging modes (spectrograph and infrared).
        Satellites turn to directions, switch on instruments, calibrate instruments, and take images.
        Ensure backward compatibility with legacy single-mode problems.
        """,
        initial_domain_pddl="""(define (domain satellite)
  (:requirements :strips :typing)
  (:types satellite direction instrument mode - object)
  (:predicates
    (on-board ?i - instrument ?s - satellite)
    (supports ?i - instrument ?m - mode)
    (pointing ?s - satellite ?d - direction)
    (power-avail ?s - satellite)
    (power-on ?i - instrument)
    (calibrated ?i - instrument)
    (have-image ?d - direction ?m - mode)
  )

  (:action turn-to
    :parameters (?s - satellite ?d-new - direction ?d-prev - direction)
    :precondition (and (pointing ?s ?d-prev))
    :effect (and (pointing ?s ?d-new) (not (pointing ?s ?d-prev)))
  )

  (:action switch-on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-avail ?s))
    :effect (and (power-on ?i) (not (power-avail ?s)) (not (calibrated ?i)))
  )

  (:action take-image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing ?s ?d))
    :effect (have-image ?d ?m)
  )
)""",
        initial_problem_pddl="""(define (problem sat_prob_01)
  (:domain satellite)
  (:objects
    sat1 - satellite
    dir1 dir2 - direction
    inst1 - instrument
    spectrograph - mode
  )
  (:init
    (on-board inst1 sat1)
    (supports inst1 spectrograph)
    (pointing sat1 dir1)
    (power-avail sat1)
    (power-on inst1)
    (calibrated inst1)
  )
  (:goal (have-image dir2 spectrograph))
)""",
        ground_truth_domain_pddl="""(define (domain satellite)
  (:requirements :strips :typing)
  (:types satellite direction instrument mode - object)
  (:predicates
    (on-board ?i - instrument ?s - satellite)
    (supports ?i - instrument ?m - mode)
    (pointing ?s - satellite ?d - direction)
    (power-avail ?s - satellite)
    (power-on ?i - instrument)
    (calibrated ?i - instrument)
    (have-image ?d - direction ?m - mode)
  )

  (:action turn-to
    :parameters (?s - satellite ?d-new - direction ?d-prev - direction)
    :precondition (and (pointing ?s ?d-prev))
    :effect (and (pointing ?s ?d-new) (not (pointing ?s ?d-prev)))
  )

  (:action switch-on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-avail ?s))
    :effect (and (power-on ?i) (not (power-avail ?s)) (not (calibrated ?i)))
  )

  (:action take-image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing ?s ?d))
    :effect (have-image ?d ?m)
  )
)""",
        ground_truth_problem_pddl="""(define (problem sat_prob_01)
  (:domain satellite)
  (:objects
    sat1 - satellite
    dir1 dir2 - direction
    inst1 - instrument
    spectrograph infrared - mode
  )
  (:init
    (on-board inst1 sat1)
    (supports inst1 spectrograph)
    (supports inst1 infrared)
    (pointing sat1 dir1)
    (power-avail sat1)
    (power-on inst1)
    (calibrated inst1)
  )
  (:goal (and (have-image dir2 spectrograph) (have-image dir1 infrared)))
)"""
    )
]
