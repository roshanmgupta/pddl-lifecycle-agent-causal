(define (domain depot-templates)
  (:requirements :strips :typing)

  (:types
    locatable object place - object
    depot distributor - place
    hoist surface truck - locatable
    crate pallet - surface
  )

  (:predicates
    (at ?x - locatable ?y - place)
    (available ?x - hoist)
    (clear ?x - surface)
    (on ?x - surface ?y - surface)
    (lifting ?x - hoist ?y - crate)
    (in ?x - crate ?y - truck)
  )

  (:action drive
    :parameters (?a - truck ?b - place ?c - place)
    :precondition (at ?a ?b)
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action lift
    :parameters (?a - hoist ?b - crate ?c - surface ?d - place)
    :precondition (and (at ?a ?d) (available ?a) (at ?b ?d) (on ?b ?c) (clear ?b))
    :effect (and (lifting ?a ?b) (clear ?c) (not (at ?b ?d)) (not (clear ?b)) (not (available ?a)) (not (on ?b ?c)))
  )

  (:action drop
    :parameters (?a - hoist ?b - crate ?c - surface ?d - place)
    :precondition (and (at ?a ?d) (at ?c ?d) (clear ?c) (lifting ?a ?b))
    :effect (and (available ?a) (at ?b ?d) (clear ?b) (on ?b ?c) (not (lifting ?a ?b)) (not (clear ?c)))
  )

  (:action load
    :parameters (?a - hoist ?b - crate ?c - truck ?d - place)
    :precondition (and (at ?a ?d) (at ?c ?d) (lifting ?a ?b))
    :effect (and (in ?b ?c) (available ?a) (not (lifting ?a ?b)))
  )

  (:action unload
    :parameters (?a - hoist ?b - crate ?c - truck ?d - place)
    :precondition (and (at ?a ?d) (at ?c ?d) (available ?a) (in ?b ?c))
    :effect (and (lifting ?a ?b) (not (in ?b ?c)) (not (available ?a)))
  )

)