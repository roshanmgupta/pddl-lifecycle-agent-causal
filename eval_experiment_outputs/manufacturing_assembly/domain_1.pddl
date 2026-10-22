(define (domain manufacturing_assembly)
  (:requirements :strips :typing)

  (:types
    assembly fixture part tool toolpool - object
    subcomponent - part
  )

  (:predicates
    (available ?p - part)
    (installed ?p - part ?a - assembly)
    (requires_tool ?p - part ?t - tool)
    (requires_fixture ?p - part ?f - fixture)
    (tool_reserved ?t - tool)
    (fixture_reserved ?f - fixture)
    (tool_available ?t - tool)
    (fixture_available ?f - fixture)
    (in_toolpool ?t - tool ?pool - toolpool)
    (in_fixturepool ?f - fixture ?pool - toolpool)
    (precedes ?p1 - part ?p2 - part)
    (transient ?p - part)
    (removed ?p - part)
    (first_part ?p - part)
    (assembled ?a - assembly)
  )

  (:action reserve_tool
    :parameters (?t - tool ?pool - toolpool)
    :precondition (and (in_toolpool ?t ?pool) (tool_available ?t))
    :effect (and (not (tool_available ?t)) (tool_reserved ?t))
  )

  (:action release_tool
    :parameters (?t - tool ?pool - toolpool)
    :precondition (and (tool_reserved ?t) (in_toolpool ?t ?pool))
    :effect (and (not (tool_reserved ?t)) (tool_available ?t))
  )

  (:action reserve_fixture
    :parameters (?f - fixture ?pool - toolpool)
    :precondition (and (in_fixturepool ?f ?pool) (fixture_available ?f))
    :effect (and (not (fixture_available ?f)) (fixture_reserved ?f))
  )

  (:action release_fixture
    :parameters (?f - fixture ?pool - toolpool)
    :precondition (and (fixture_reserved ?f) (in_fixturepool ?f ?pool))
    :effect (and (not (fixture_reserved ?f)) (fixture_available ?f))
  )

  (:action fit_first_part
    :parameters (?p - part ?a - assembly ?t - tool ?f - fixture)
    :precondition (and (available ?p) (requires_tool ?p ?t) (requires_fixture ?p ?f) (tool_reserved ?t) (fixture_reserved ?f) (first_part ?p))
    :effect (and (not (available ?p)) (installed ?p ?a))
  )

  (:action fit_subsequent_part
    :parameters (?p - part ?a - assembly ?t - tool ?f - fixture ?prev - part)
    :precondition (and (available ?p) (requires_tool ?p ?t) (requires_fixture ?p ?f) (tool_reserved ?t) (fixture_reserved ?f) (precedes ?prev ?p) (installed ?prev ?a))
    :effect (and (not (available ?p)) (installed ?p ?a))
  )

  (:action fit_after_removal
    :parameters (?p - part ?a - assembly ?t - tool ?f - fixture ?prev - part)
    :precondition (and (available ?p) (requires_tool ?p ?t) (requires_fixture ?p ?f) (tool_reserved ?t) (fixture_reserved ?f) (precedes ?prev ?p) (removed ?prev))
    :effect (and (not (available ?p)) (installed ?p ?a))
  )

  (:action remove_transient
    :parameters (?p - part ?a - assembly)
    :precondition (and (transient ?p) (installed ?p ?a))
    :effect (and (not (installed ?p ?a)) (removed ?p))
  )

  (:action complete_assembly
    :parameters (?a - assembly ?final - part)
    :precondition (installed ?final ?a)
    :effect (assembled ?a)
  )

)