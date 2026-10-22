(define (domain depots_domain)
  (:requirements :strips :typing)

  (:types
    clearable crate depot distributor hoist location pallet surface truck - object
  )

  (:predicates
    (at_truck ?t - truck ?d - location)
    (at_hoist ?h - hoist ?d - location)
    (on ?c - crate ?s - surface)
    (at_crate ?c - crate ?d - location)
    (clear ?s - clearable)
    (loaded ?c - crate ?t - truck)
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?d - location ?s - surface)
    :precondition (and (at_hoist ?h ?d) (at_truck ?t ?d) (at_crate ?c ?d) (on ?c ?s) (clear ?s) (clear ?h))
    :effect (and (loaded ?c ?t) (not (at_crate ?c ?d)) (not (on ?c ?s)) (clear ?s))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?d - location)
    :precondition (and (at_hoist ?h ?d) (at_truck ?t ?d) (loaded ?c ?t))
    :effect (and (at_crate ?c ?d) (not (loaded ?c ?t)))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?d - location)
    :precondition (and (at_hoist ?h ?d) (on ?c ?s) (clear ?s) (at_crate ?c ?d))
    :effect (and (clear ?s) (not (on ?c ?s)))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?d - location)
    :precondition (and (at_hoist ?h ?d) (clear ?s) (at_crate ?c ?d))
    :effect (and (on ?c ?s) (not (clear ?s)))
  )

)