(define (domain logistics_warehouse)
  (:requirements :strips :typing)

  (:types
    hoist surface truck - locatable
    crate pallet - surface
    locatable location - object
  )

  (:predicates
    (at ?x - locatable ?l - location)
    (on ?c - crate ?s - surface)
    (loaded ?c - crate ?t - truck)
    (empty ?t - truck)
  )

  (:action load
    :parameters (?c - crate ?t - truck ?l - location ?h - hoist ?s - surface)
    :precondition (and (at ?c ?l) (at ?t ?l) (at ?h ?l) (on ?c ?s) (empty ?t))
    :effect (and (loaded ?c ?t) (not (on ?c ?s)) (not (empty ?t)))
  )

  (:action unload
    :parameters (?c - crate ?t - truck ?l - location ?h - hoist ?s - surface)
    :precondition (and (loaded ?c ?t) (at ?t ?l) (at ?h ?l) (at ?s ?l))
    :effect (and (on ?c ?s) (not (loaded ?c ?t)) (empty ?t))
  )

  (:action lift
    :parameters (?c - crate ?l - location ?h - hoist ?s - surface)
    :precondition (and (on ?c ?s) (at ?c ?l) (at ?h ?l))
    :effect (and (not (on ?c ?s)) (not (at ?c ?l)))
  )

  (:action drop
    :parameters (?c - crate ?l - location ?h - hoist ?s - surface)
    :precondition (and (at ?h ?l) (at ?s ?l))
    :effect (and (on ?c ?s) (at ?c ?l))
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

)