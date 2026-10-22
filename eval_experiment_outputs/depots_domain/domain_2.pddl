(define (domain depots_domain)
  (:requirements :strips :typing)

  (:types
    crate hoist surface truck - locatable
    depot distributor - location
    pallet - surface
    locatable location - object
  )

  (:predicates
    (at ?x - locatable ?l - location)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location ?s - surface)
    :precondition (and (at ?h ?l) (at ?t ?l) (available ?h) (on ?c ?s) (at ?s ?l))
    :effect (and (not (available ?h)) (not (on ?c ?s)) (in ?c ?t) (lifting ?h ?c))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location ?s - surface)
    :precondition (and (at ?h ?l) (at ?t ?l) (lifting ?h ?c) (in ?c ?t))
    :effect (and (available ?h) (not (lifting ?h ?c)) (not (in ?c ?t)) (on ?c ?s) (at ?s ?l))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (available ?h) (on ?c ?s) (at ?s ?l))
    :effect (and (not (available ?h)) (not (on ?c ?s)) (lifting ?h ?c))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (lifting ?h ?c) (at ?s ?l))
    :effect (and (available ?h) (not (lifting ?h ?c)) (on ?c ?s))
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

)