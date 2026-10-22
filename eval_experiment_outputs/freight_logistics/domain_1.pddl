(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    crate entity hoist location pallet truck - object
  )

  (:predicates
    (at ?t - truck ?l - location)
    (at ?c - crate ?l - location)
    (on ?c - crate ?p - pallet)
    (on ?c1 - crate ?c2 - crate)
    (loaded ?c - crate ?t - truck)
    (empty ?t - truck)
    (holding ?h - hoist ?c - crate)
    (available ?h - hoist)
    (at ?p - pallet ?l - location)
    (at ?e - entity ?l - location)
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (at ?c ?l) (holding ?h ?c) (empty ?t))
    :effect (and (not (holding ?h ?c)) (not (at ?c ?l)) (loaded ?c ?t) (not (empty ?t)))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (loaded ?c ?t) (available ?h))
    :effect (and (holding ?h ?c) (not (loaded ?c ?t)) (empty ?t) (at ?c ?l))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?p - pallet ?l - location)
    :precondition (and (at ?c ?l) (on ?c ?p) (available ?h))
    :effect (and (holding ?h ?c) (not (on ?c ?p)) (not (available ?h)))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?p - pallet ?l - location)
    :precondition (and (holding ?h ?c) (at ?p ?l))
    :effect (and (on ?c ?p) (not (holding ?h ?c)) (available ?h))
  )

  (:action stack
    :parameters (?h - hoist ?c1 - crate ?c2 - crate ?l - location)
    :precondition (and (holding ?h ?c1) (at ?c2 ?l))
    :effect (and (on ?c1 ?c2) (not (holding ?h ?c1)) (available ?h))
  )

)