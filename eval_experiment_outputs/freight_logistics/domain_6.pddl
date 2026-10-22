(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    crate hoist location pallet truck - object
    depot - location
    urgent_cargo - crate
  )

  (:predicates
    (at-truck ?t - truck ?l - location)
    (at-crate ?c - crate ?l - location)
    (on ?c1 - crate ?c2 - crate)
    (on-pallet ?c - crate ?p - pallet)
    (loaded ?c - crate ?t - truck)
    (hoist-at ?h - hoist ?l - location)
    (empty-hoist ?h - hoist)
    (at-pallet ?p - pallet ?l - location)
    (urgent ?c - urgent_cargo)
  )

  (:action move-truck
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at-truck ?t ?from) (not (at-truck ?t ?to)))
    :effect (and (not (at-truck ?t ?from)) (at-truck ?t ?to))
  )

  (:action express-transit
    :parameters (?t - truck ?from - depot ?to - depot ?c - urgent_cargo)
    :precondition (and (at-truck ?t ?from) (not (at-truck ?t ?to)) (loaded ?c ?t) (urgent ?c))
    :effect (and (not (at-truck ?t ?from)) (at-truck ?t ?to))
  )

  (:action load-crate
    :parameters (?c - crate ?t - truck ?h - hoist ?l - location)
    :precondition (and (at-truck ?t ?l) (at-crate ?c ?l) (hoist-at ?h ?l) (empty-hoist ?h))
    :effect (and (loaded ?c ?t) (not (at-crate ?c ?l)) (not (empty-hoist ?h)))
  )

  (:action unload-crate
    :parameters (?c - crate ?t - truck ?h - hoist ?l - location)
    :precondition (and (at-truck ?t ?l) (loaded ?c ?t) (hoist-at ?h ?l) (not (empty-hoist ?h)))
    :effect (and (at-crate ?c ?l) (not (loaded ?c ?t)) (empty-hoist ?h))
  )

  (:action stack-crate
    :parameters (?c1 - crate ?c2 - crate ?h - hoist ?l - location)
    :precondition (and (at-crate ?c1 ?l) (at-crate ?c2 ?l) (hoist-at ?h ?l) (empty-hoist ?h) (not (on ?c1 ?c2)))
    :effect (and (on ?c1 ?c2) (not (at-crate ?c1 ?l)) (not (empty-hoist ?h)))
  )

  (:action unstack-crate
    :parameters (?c1 - crate ?c2 - crate ?h - hoist ?l - location)
    :precondition (and (on ?c1 ?c2) (hoist-at ?h ?l) (not (empty-hoist ?h)))
    :effect (and (at-crate ?c1 ?l) (not (on ?c1 ?c2)) (empty-hoist ?h))
  )

  (:action move-hoist
    :parameters (?h - hoist ?from - location ?to - location)
    :precondition (and (hoist-at ?h ?from) (not (hoist-at ?h ?to)))
    :effect (and (not (hoist-at ?h ?from)) (hoist-at ?h ?to))
  )

)