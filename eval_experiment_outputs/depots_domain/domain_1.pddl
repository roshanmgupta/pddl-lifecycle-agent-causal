(define (domain depots_domain)
  (:requirements :strips :typing)

  (:types
    crate surface truck - locatable
    hoist locatable location - object
    pallet - surface
    depot distributor - location
  )

  (:predicates
    (at ?x - locatable ?l - location)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
    (available ?h - hoist)
    (clear ?s - surface)
    (holding ?h - hoist ?c - crate)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (at ?c ?l) (on ?c ?s) (available ?h) (clear ?c))
    :effect (and (not (on ?c ?s)) (not (clear ?c)) (clear ?s) (not (available ?h)) (holding ?h ?c))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (at ?s ?l) (holding ?h ?c) (clear ?s))
    :effect (and (not (holding ?h ?c)) (on ?c ?s) (clear ?c) (available ?h) (not (clear ?s)))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?h ?l) (at ?t ?l) (holding ?h ?c))
    :effect (and (not (holding ?h ?c)) (in ?c ?t) (available ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?h ?l) (at ?t ?l) (available ?h) (in ?c ?t))
    :effect (and (holding ?h ?c) (not (in ?c ?t)) (not (available ?h)))
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

)