(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    hoist surface truck - locatable
    crate pallet - surface
    locatable location - object
  )

  (:predicates
    (at ?x - locatable ?l - location)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
    (empty ?h - hoist)
    (holding ?h - hoist ?c - crate)
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?h ?l) (at ?t ?l) (holding ?h ?c))
    :effect (and (not (holding ?h ?c)) (in ?c ?t) (empty ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?l - location)
    :precondition (and (at ?h ?l) (at ?t ?l) (empty ?h) (in ?c ?t))
    :effect (and (not (in ?c ?t)) (holding ?h ?c) (not (empty ?h)))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (at ?s ?l) (on ?c ?s) (empty ?h))
    :effect (and (not (on ?c ?s)) (holding ?h ?c) (not (empty ?h)))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?l - location)
    :precondition (and (at ?h ?l) (at ?s ?l) (holding ?h ?c))
    :effect (and (not (holding ?h ?c)) (on ?c ?s) (empty ?h))
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

)