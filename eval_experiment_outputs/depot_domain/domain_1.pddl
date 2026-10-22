(define (domain depot_domain)
  (:requirements :strips :typing)

  (:types
    crate hoist place surface truck - object
    pallet - surface
  )

  (:predicates
    (at ?x - object ?y - place)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (clear ?x - object)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
    (pallet ?p - pallet)
    (surface ?s - surface)
    (truck ?t - truck)
    (place ?p - place)
    (hoist ?h - hoist)
    (crate ?c - crate)
  )

  (:action drive
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (available ?h) (at ?c ?p) (on ?c ?s) (clear ?c))
    :effect (and (not (available ?h)) (lifting ?h ?c) (not (at ?c ?p)) (not (on ?c ?s)) (not (clear ?c)) (clear ?s))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (lifting ?h ?c) (at ?s ?p) (clear ?s))
    :effect (and (available ?h) (not (lifting ?h ?c)) (at ?c ?p) (on ?c ?s) (clear ?c) (not (clear ?s)))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (lifting ?h ?c) (at ?t ?p))
    :effect (and (available ?h) (not (lifting ?h ?c)) (in ?c ?t))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (available ?h) (at ?t ?p) (in ?c ?t))
    :effect (and (not (available ?h)) (lifting ?h ?c) (not (in ?c ?t)))
  )

)