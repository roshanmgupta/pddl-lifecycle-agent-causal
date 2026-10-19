import os
from pathlib import Path
from typing import List
from benchmark.schema import BenchmarkTask, LifecycleTaskType

BASE_DIR = Path(__file__).resolve().parent.parent

def load_pddl_file(rel_path: str, fallback_str: str = "") -> str:
    """Loads a PDDL domain or problem file directly from the benchmark dataset folder."""
    full_path = BASE_DIR / rel_path
    if full_path.exists():
        try:
            content = full_path.read_text(encoding="utf-8").strip()
            if content:
                return content
        except Exception as e:
            print(f"[WARN]: Error reading {full_path}: {e}")
    else:
        print(f"[WARNING]: Benchmark file missing at '{full_path}'! Metric calculations may be skewed.")
    return fallback_str.strip()

BENCHMARK_TASKS: List[BenchmarkTask] = [

    # =========================================================================
    # 1. DEPOTS DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 1.1 Elicitation Task
    BenchmarkTask(
        task_id="depots_elicit_01",
        domain_family="depots",
        task_type=LifecycleTaskType.ELICITATION,
        title="Depots Logistics & Stacking Domain Elicitation",
        natural_language_requirements="""
        A depots domain combining logistics and block stacking mechanics.
        Trucks carry crates between depots and distributors.
        Hoists lift crates from trucks, pallets, or other crates and drop them onto pallets or crates.
        Hoists can also load and unload crates into trucks.
        Define scenario with truck t1, hoist h1 at depot d1, crate c1 on pallet p1 at d1.
        The goal is to have crate c1 loaded into truck t1.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 1.2 Synthetic Fault Repair Task (Unbound Variable Error)
    BenchmarkTask(
        task_id="depots_repair_unbound_var_01",
        domain_family="depots",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="Depots Repair: Unbound Variable in drop Action",
        fault_category="TYPE_SIGNATURE",
        gold_fault_element="drop",
        natural_language_requirements="Hoists drop crates onto pallets or surfaces. All parameters must be bound.",
        initial_domain_pddl="""(define (domain depot)
  (:requirements :typing)
  (:types place locatable - object
          depot distributor - place
          truck hoist surface - locatable
          pallet crate - surface)
  (:predicates
    (at ?x - locatable ?p - place)
    (on ?c - crate ?s - surface)
    (lifting ?h - hoist ?c - crate)
    (available ?h - hoist)
    (clear ?s - surface)
  )

  (:action drop
    :parameters (?x - hoist ?y - crate ?z - surface ?p - place)
    :precondition (and (at ?x ?p) (at ?z ?p) (clear ?z) (lifting ?x ?y))
    :effect (and (available ?x) (not (lifting ?x ?y)) (at ?y ?p) (not (clear ?z)) (clear ?y) (on ?y ?z))
  )

  (:action lift
    :parameters (?x - hoist ?y - crate ?z - surface ?p - place)
    :precondition (and (at ?x ?p) (available ?x) (at ?y ?p) (on ?y ?z) (clear ?y))
    :effect (and (not (at ?y ?p)) (lifting ?x ?y) (not (clear ?y)) (not (available ?x)) (clear ?z) (not (on ?y ?z)))
  )
)""",
        initial_problem_pddl="""(define (problem depot_prob_01)
  (:domain depot)
  (:objects d1 - depot h1 - hoist c1 - crate p1 - pallet)
  (:init (at h1 d1) (at p1 d1) (at c1 d1) (on c1 p1) (clear c1) (available h1))
  (:goal (lifting h1 c1))
)""",
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 1.3 Domain Evolution Task (Dual Hoist Capacity)
    BenchmarkTask(
        task_id="depots_evolve_01",
        domain_family="depots",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="Depots Evolution: Dual Hoist Operational Capacity",
        natural_language_requirements="""
        Extend Depots domain to manage multiple independent hoists at each depot simultaneously.
        Ensure backward compatibility with single-hoist historical problems.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/depots-strips-automatic/instances/instance-2.pddl")
    ),

    # =========================================================================
    # 2. DRIVERLOG DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 2.1 Elicitation Task
    BenchmarkTask(
        task_id="driverlog_elicit_01",
        domain_family="driverlog",
        task_type=LifecycleTaskType.ELICITATION,
        title="DriverLog Domain & Problem Elicitation",
        natural_language_requirements="""
        A transportation logistics network where delivery trucks must be driven by licensed human drivers.
        Drivers walk between path-connected locations or board trucks to drive them along road networks between locations.
        Trucks are used to load, transport, and unload packages between warehouse docks and delivery addresses.
        Define scenario with drivers driver1 and driver2 at location s2, trucks truck1 and truck2 at location s0,
        packages package1 and package2 at s0, path and road connections between s0, s1, and s2.
        The goal is to deliver package1 to s1 and package2 to s0.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 2.2 Synthetic Fault Repair Task (Missing Driving Precondition in DRIVE-TRUCK)
    BenchmarkTask(
        task_id="driverlog_repair_driving_condition_01",
        domain_family="driverlog",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="DriverLog Repair: Missing (driving ?driver ?truck) Precondition in DRIVE-TRUCK",
        fault_category="GROUNDING_UNSOLVABILITY",
        gold_fault_element="DRIVE-TRUCK",
        natural_language_requirements="Driving a truck requires the driver to be actively driving that specific truck.",
        initial_domain_pddl="""(define (domain driverlog)
  (:requirements :typing)
  (:types location locatable - object
          driver truck obj - locatable)
  (:predicates
    (at ?obj - locatable ?loc - location)
    (in ?obj1 - obj ?obj - truck)
    (driving ?d - driver ?v - truck)
    (link ?x ?y - location)
    (path ?x ?y - location)
    (empty ?v - truck)
  )

  (:action LOAD-TRUCK
    :parameters (?obj - obj ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (at ?obj ?loc))
    :effect (and (not (at ?obj ?loc)) (in ?obj ?truck))
  )

  (:action UNLOAD-TRUCK
    :parameters (?obj - obj ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (in ?obj ?truck))
    :effect (and (not (in ?obj ?truck)) (at ?obj ?loc))
  )

  (:action BOARD-TRUCK
    :parameters (?driver - driver ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (at ?driver ?loc) (empty ?truck))
    :effect (and (not (at ?driver ?loc)) (driving ?driver ?truck) (not (empty ?truck)))
  )

  (:action DISEMBARK-TRUCK
    :parameters (?driver - driver ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (driving ?driver ?truck))
    :effect (and (not (driving ?driver ?truck)) (at ?driver ?loc) (empty ?truck))
  )

  (:action DRIVE-TRUCK
    :parameters (?truck - truck ?loc-from - location ?loc-to - location ?driver - driver)
    :precondition (and (at ?truck ?loc-from) (link ?loc-from ?loc-to)) ;; FAULT: Missing (driving ?driver ?truck)!
    :effect (and (not (at ?truck ?loc-from)) (at ?truck ?loc-to))
  )

  (:action WALK
    :parameters (?driver - driver ?loc-from - location ?loc-to - location)
    :precondition (and (at ?driver ?loc-from) (path ?loc-from ?loc-to))
    :effect (and (not (at ?driver ?loc-from)) (at ?driver ?loc-to))
  )
)""",
        initial_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/instances/instance-1.pddl"
        ),
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 2.3 Domain Evolution Task (Multi-Trailer Logistics Extension)
    BenchmarkTask(
        task_id="driverlog_evolve_01",
        domain_family="driverlog",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="DriverLog Evolution: Express Road Transit",
        natural_language_requirements="""
        Extend DriverLog domain to support high-throughput express delivery between distribution centers.
        Ensure backward compatibility with standard historical driver logistics problems.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/driverlog-strips-automatic/instances/instance-2.pddl")
    ),

    # =========================================================================
    # 3. ZENOTRAVEL DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 3.1 Elicitation Task
    BenchmarkTask(
        task_id="zenotravel_elicit_01",
        domain_family="zenotravel",
        task_type=LifecycleTaskType.ELICITATION,
        title="ZenoTravel Flight Operations & Fuel Elicitation",
        natural_language_requirements="""
        An air passenger transportation network with aircraft, passengers, cities, and discrete fuel levels.
        Passengers can board and debark aircraft at cities.
        Aircraft can fly between cities if at the departure city, consuming one discrete fuel level from current to next lower fuel level.
        Aircraft can zoom at supersonic speed between cities, consuming two discrete fuel levels.
        Aircraft can refuel at a city, transitioning from current fuel level to next higher level.
        Define scenario with aircraft plane1 at city0 with fuel level fl1, passengers person1 at city0 and person2 at city2, cities city0..city2, and fuel levels fl0..fl6.
        Goal is plane1 at city1, person1 at city0, and person2 at city2.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 3.2 Synthetic Fault Repair Task (Missing Fuel Condition in fly)
    BenchmarkTask(
        task_id="zenotravel_repair_fuel_condition_01",
        domain_family="zenotravel",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="ZenoTravel Repair: Missing Fuel Level Precondition in fly Action",
        fault_category="GROUNDING_UNSOLVABILITY",
        gold_fault_element="fly",
        natural_language_requirements="Flying an aircraft requires it to have an active fuel level and consumes fuel to the next level.",
        initial_domain_pddl="""(define (domain zeno-travel)
  (:requirements :typing)
  (:types aircraft person city flevel - object)
  (:predicates
    (at ?x - (either person aircraft) ?c - city)
    (in ?p - person ?a - aircraft)
    (fuel-level ?a - aircraft ?l - flevel)
    (next ?l1 ?l2 - flevel)
  )

  (:action board
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (at ?p ?c) (at ?a ?c))
    :effect (and (not (at ?p ?c)) (in ?p ?a))
  )

  (:action debark
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (in ?p ?a) (at ?a ?c))
    :effect (and (not (in ?p ?a)) (at ?p ?c))
  )

  (:action fly
    :parameters (?a - aircraft ?c1 ?c2 - city ?l1 ?l2 - flevel)
    :precondition (and (at ?a ?c1) (next ?l2 ?l1))  ;; FAULT: Missing (fuel-level ?a ?l1)!
    :effect (and (not (at ?a ?c1)) (at ?a ?c2) (not (fuel-level ?a ?l1)) (fuel-level ?a ?l2))
  )

  (:action refuel
    :parameters (?a - aircraft ?c - city ?l - flevel ?l1 - flevel)
    :precondition (and (fuel-level ?a ?l) (next ?l ?l1) (at ?a ?c))
    :effect (and (fuel-level ?a ?l1) (not (fuel-level ?a ?l)))
  )
)""",
        initial_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/instances/instance-1.pddl"
        ),
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 3.3 Domain Evolution Task (Inter-City Flight Scheduling)
    BenchmarkTask(
        task_id="zenotravel_evolve_01",
        domain_family="zenotravel",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="ZenoTravel Evolution: Multi-Leg Long-Haul Flight Routes",
        natural_language_requirements="""
        Extend ZenoTravel domain to handle multi-leg cross-country transit with strict fuel conservation.
        Ensure backward compatibility with regional historical flight instances.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/zenotravel-strips-automatic/instances/instance-2.pddl")
    ),

    # =========================================================================
    # 4. SATELLITE DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 4.1 Elicitation Task
    BenchmarkTask(
        task_id="satellite_elicit_01",
        domain_family="satellite",
        task_type=LifecycleTaskType.ELICITATION,
        title="Satellite Earth Observation Domain Elicitation",
        natural_language_requirements="""
        Satellite observation domain with satellites, instruments, modes, and directions.
        Satellites turn between directions.
        Satellites turn on instruments if instrument is on-board and power is available.
        Instruments can be calibrated pointing at calibration target direction.
        Satellites take image of direction in mode if pointing at direction, instrument is on, calibrated, and supports mode.
        Define scenario with satellite sat1 pointing at dir1, instrument inst1 supporting thermograph, goal is image of dir2 in thermograph.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 4.2 Synthetic Fault Repair Task (Missing Power Condition)
    BenchmarkTask(
        task_id="satellite_repair_power_01",
        domain_family="satellite",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="Satellite Repair: Missing power-avail Precondition in switch-on",
        fault_category="GROUNDING_UNSOLVABILITY",
        gold_fault_element="switch-on",
        natural_language_requirements="Turning on an instrument requires power to be available on satellite.",
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

  (:action switch-on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s)) ;; FAULT: Missing (power-avail ?s)!
    :effect (and (power-on ?i) (not (power-avail ?s)) (not (calibrated ?i)))
  )

  (:action switch-off
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-on ?i))
    :effect (and (not (power-on ?i)) (power-avail ?s))
  )

  (:action take-image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing ?s ?d))
    :effect (have-image ?d ?m)
  )
)""",
        initial_problem_pddl="""(define (problem sat_prob_power)
  (:domain satellite)
  (:objects sat1 - satellite dir1 dir2 - direction inst1 inst2 - instrument mode1 - mode)
  (:init (on-board inst1 sat1) (on-board inst2 sat1) (power-avail sat1) (pointing sat1 dir1))
  (:goal (and (power-on inst1) (power-on inst2))) ;; Unsolvable if only 1 power unit exists!
)""",
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 4.3 Domain Evolution Task (Adding Infrared Imaging Mode)
    BenchmarkTask(
        task_id="satellite_evolve_01",
        domain_family="satellite",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="Satellite Evolution: Dual Imaging Modes",
        natural_language_requirements="""
        Extend existing Satellite domain to support dual imaging modes (spectrograph and infrared).
        Ensure backward compatibility with legacy single-mode problems.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/satellite-strips-automatic/instances/instance-2.pddl")
    ),

    # =========================================================================
    # 5. ROVERS DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 5.1 Elicitation Task
    BenchmarkTask(
        task_id="rovers_elicit_01",
        domain_family="rovers",
        task_type=LifecycleTaskType.ELICITATION,
        title="Rovers Planetary Exploration Domain & Problem Elicitation",
        natural_language_requirements="""
        A planetary exploration domain with autonomous rovers, waypoints, stores, cameras, modes, landers, and objectives.
        Rovers navigate between connected waypoints.
        Rovers equipped with soil analysis can sample soil at a waypoint if the rover store is empty.
        Rovers equipped with rock analysis can sample rock at a waypoint if the rover store is empty.
        Rovers can drop samples from their store to empty it.
        Rovers can calibrate cameras pointing at calibration target objectives.
        Rovers can take images of objectives in specific modes if camera is calibrated, on board, and mode is supported.
        Rovers can communicate soil, rock, and image data to a lander if at a waypoint with line-of-sight to lander.
        Define a scenario with lander general at waypoint0, rover0 with camera0 at waypoint3, waypoint0..3, and communicate soil data from waypoint2.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 5.2 Synthetic Fault Repair Task (Missing store empty precondition)
    BenchmarkTask(
        task_id="rovers_repair_store_01",
        domain_family="rovers",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="Rovers Repair: Missing (empty ?s) Precondition in sample_soil",
        fault_category="GROUNDING_UNSOLVABILITY",
        gold_fault_element="sample_soil",
        natural_language_requirements="Rovers soil sampling requires the rover store to be empty before collecting a new sample.",
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/domain.pddl").replace(
            "(store_of ?s ?x) (empty ?s)",
            "(store_of ?s ?x)"  # FAULT: Missing (empty ?s)!
        ),
        initial_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/instances/instance-1.pddl"
        ),
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 5.3 Domain Evolution Task (Enhanced Direct Uplink)
    BenchmarkTask(
        task_id="rovers_evolve_01",
        domain_family="rovers",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="Rovers Evolution: High-Gain Direct Satellite Uplink",
        natural_language_requirements="""
        Extend Rovers domain to support direct satellite uplink communication channels.
        Ensure backward compatibility with historical lander communication instances.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/rovers-strips-automatic/instances/instance-2.pddl")
    ),

    # =========================================================================
    # 6. FREECELL DOMAIN FAMILY (IPC-2002 Typed)
    # =========================================================================

    # 6.1 Elicitation Task
    BenchmarkTask(
        task_id="freecell_elicit_01",
        domain_family="freecell",
        task_type=LifecycleTaskType.ELICITATION,
        title="FreeCell Solitaire Domain & Problem Elicitation",
        natural_language_requirements="""
        A card game solitaire domain with cards, suits, denominations, columns, and free cells.
        Cards can be moved to an empty free cell if free cells are available.
        Cards can be moved from a free cell or column to a home cell if of the same suit and in ascending numerical sequence.
        Cards can be moved between columns if the target column card has opposite suit color and one denomination higher.
        Define scenario with 2 free cells, 4 columns, denominations N0 to N4, suits diamond, club, heart, spade,
        and cards spadeA, diamondA, club2, heart2, etc. Goal is to move all aces to home cells.
        """,
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 6.2 Synthetic Fault Repair Task (Missing Available Cell Condition)
    BenchmarkTask(
        task_id="freecell_repair_unbound_col_01",
        domain_family="freecell",
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title="FreeCell Repair: Missing (cellspace) Precondition in sendtofree",
        fault_category="GROUNDING_UNSOLVABILITY",
        gold_fault_element="sendtofree",
        natural_language_requirements="Moving a card to a free cell requires free cell capacity to be available.",
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/domain.pddl").replace(
            "(cellspace ?cells)",
            ""
        ),
        initial_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/instances/instance-1.pddl"
        ),
        ground_truth_domain_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/domain.pddl"
        ),
        ground_truth_problem_pddl=load_pddl_file(
            "pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/instances/instance-1.pddl"
        )
    ),

    # 6.3 Domain Evolution Task (Multi-Card Column Move Extension)
    BenchmarkTask(
        task_id="freecell_evolve_01",
        domain_family="freecell",
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title="FreeCell Evolution: Multi-Card Sequence Moves",
        natural_language_requirements="""
        Extend FreeCell domain to support multi-card sequence moves between columns.
        Ensure backward compatibility with single-card moves and historical game instances.
        """,
        initial_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/domain.pddl"),
        initial_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/instances/instance-2.pddl"),
        ground_truth_domain_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/domain.pddl"),
        ground_truth_problem_pddl=load_pddl_file("pddl_benchmark_instances/ipc-2002/domains/freecell-strips-automatic/instances/instance-2.pddl")
    )
]
