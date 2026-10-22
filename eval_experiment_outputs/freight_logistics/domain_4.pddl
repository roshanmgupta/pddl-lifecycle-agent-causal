(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    hoist location movable - object
    crate pallet truck - movable
  )

  (:predicates
    (at_movable ?m - movable ?l - location)
    (on_crate ?c1 - crate ?c2 - crate)
    (on_pallet ?c - crate ?p - pallet)
    (loaded ?c - crate ?t - truck)
    (empty ?t - truck)
    (holding ?h - hoist ?c - crate)
  )

  (:action move_truck
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at_movable ?t ?from)
    :effect (and (not (at_movable ?t ?from)) (at_movable ?t ?to))
  )

  (:action load_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at_movable ?t ?l) (holding ?h ?c) (at_movable ?c ?l))
    :effect (and (not (holding ?h ?c)) (loaded ?c ?t) (empty ?t))
  )

  (:action unload_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at_movable ?t ?l) (loaded ?c ?t) (empty ?t))
    :effect (and (not (loaded ?c ?t)) (holding ?h ?c) (at_movable ?c ?l))
  )

  (:action stack_crate
    :parameters (?h - hoist ?c1 - crate ?c2 - crate ?l - location)
    :precondition (and (holding ?h ?c1) (at_movable ?c2 ?l))
    :effect (and (not (holding ?h ?c1)) (on_crate ?c1 ?c2))
  )

  (:action unstack_crate
    :parameters (?h - hoist ?c1 - crate ?c2 - crate ?l - location)
    :precondition (and (on_crate ?c1 ?c2) (at_movable ?c2 ?l))
    :effect (and (not (on_crate ?c1 ?c2)) (holding ?h ?c1))
  )

  (:action pick_up_crate
    :parameters (?h - hoist ?c - crate ?p - pallet ?l - location)
    :precondition (and (on_pallet ?c ?p) (at_movable ?p ?l))
    :effect (and (not (on_pallet ?c ?p)) (holding ?h ?c))
  )

)