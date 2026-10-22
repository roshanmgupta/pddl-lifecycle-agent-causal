(define (domain depot)
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
)