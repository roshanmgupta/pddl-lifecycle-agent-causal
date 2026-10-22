(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    crate hoist location pallet stackable transportable truck - object
  )

  (:predicates
    (truck_at ?t - truck ?l - location)
    (crate_at ?c - crate ?l - location)
    (on_crate_pallet ?c - crate ?p - pallet)
    (on_crate_crate ?c1 - crate ?c2 - crate)
    (loaded ?c - crate ?t - truck)
    (empty ?t - truck)
    (hoist_at ?h - hoist ?l - location)
    (holding ?h - hoist ?c - crate)
    (connected ?l1 - location ?l2 - location)
  )

  (:action move_truck
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (truck_at ?t ?from) (connected ?from ?to))
    :effect (and (not (truck_at ?t ?from)) (truck_at ?t ?to))
  )

  (:action load_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (hoist_at ?h ?l) (truck_at ?t ?l) (holding ?h ?c) (empty ?t))
    :effect (and (not (holding ?h ?c)) (loaded ?c ?t) (not (empty ?t)) (hoist_at ?h ?l))
  )

  (:action unload_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (hoist_at ?h ?l) (truck_at ?t ?l) (loaded ?c ?t))
    :effect (and (holding ?h ?c) (not (loaded ?c ?t)) (empty ?t) (hoist_at ?h ?l))
  )

  (:action stack_crate
    :parameters (?h - hoist ?c1 - crate ?c2 - crate ?l - location)
    :precondition (and (hoist_at ?h ?l) (holding ?h ?c1) (crate_at ?c2 ?l))
    :effect (and (not (holding ?h ?c1)) (on_crate_crate ?c1 ?c2) (hoist_at ?h ?l))
  )

  (:action unstack_crate
    :parameters (?h - hoist ?c1 - crate ?c2 - crate ?l - location)
    :precondition (and (hoist_at ?h ?l) (on_crate_crate ?c1 ?c2))
    :effect (and (holding ?h ?c1) (not (on_crate_crate ?c1 ?c2)) (hoist_at ?h ?l))
  )

  (:action move_crate
    :parameters (?h - hoist ?c - crate ?from - location ?to - location)
    :precondition (and (hoist_at ?h ?from) (holding ?h ?c) (connected ?from ?to))
    :effect (and (not (crate_at ?c ?from)) (crate_at ?c ?to) (hoist_at ?h ?to))
  )

)