(define (domain Depot)
  (:requirements :strips :typing)

  (:types
    locatable place - object
    depot distributor - place
    hoist surface truck - locatable
    crate pallet - surface
  )

  (:predicates
    (at ?x - locatable ?y - place)
    (on ?x - crate ?y - surface)
    (in ?x - crate ?y - truck)
    (lifting ?x - hoist ?y - crate)
    (available ?x - hoist)
    (clear ?x - surface)
    (needs-maintenance ?x - hoist)
  )

  (:action Drive
    :parameters (?x - truck ?y - place ?z - place)
    :precondition (at ?x ?y)
    :effect (and (not (at ?x ?y)) (at ?x ?z))
  )

  (:action Lift
    :parameters (?x - hoist ?y - crate ?z - surface ?p - place)
    :precondition (and (at ?x ?p) (available ?x) (at ?y ?p) (on ?y ?z) (clear ?y))
    :effect (and (not (at ?y ?p)) (lifting ?x ?y) (not (clear ?y)) (not (available ?x)) (clear ?z) (not (on ?y ?z)))
  )

  (:action Drop
    :parameters (?x - hoist ?y - crate ?z - surface ?p - place)
    :precondition (and (at ?x ?p) (at ?z ?p) (clear ?z) (lifting ?x ?y))
    :effect (and (available ?x) (not (lifting ?x ?y)) (at ?y ?p) (not (clear ?z)) (clear ?y) (on ?y ?z) (needs-maintenance ?x))
  )

  (:action Load
    :parameters (?x - hoist ?y - crate ?z - truck ?p - place)
    :precondition (and (at ?x ?p) (at ?z ?p) (lifting ?x ?y))
    :effect (and (not (lifting ?x ?y)) (in ?y ?z) (available ?x) (needs-maintenance ?x))
  )

  (:action Unload
    :parameters (?x - hoist ?y - crate ?z - truck ?p - place)
    :precondition (and (at ?x ?p) (at ?z ?p) (available ?x) (in ?y ?z))
    :effect (and (not (in ?y ?z)) (not (available ?x)) (lifting ?x ?y))
  )

  (:action Service-hoist
    :parameters (?x - hoist)
    :precondition (needs-maintenance ?x)
    :effect (and (not (needs-maintenance ?x)) (available ?x))
  )

)