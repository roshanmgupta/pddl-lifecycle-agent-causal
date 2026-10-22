(define (domain depots_logistics_blocks)
  (:requirements :strips :typing)

  (:types
    hoist object place surface truck - object
    depot distributor - place
    crate pallet - surface
  )

  (:predicates
    (at ?x - object ?p - place)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
    (lifting ?h - hoist ?c - crate)
    (available ?h - hoist)
    (clear ?s - surface)
  )

  (:action drive
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?c ?p) (on ?c ?s) (available ?h) (clear ?c))
    :effect (and (not (on ?c ?s)) (not (clear ?c)) (lifting ?h ?c) (not (available ?h)) (clear ?s))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (lifting ?h ?c))
    :effect (and (not (lifting ?h ?c)) (in ?c ?t) (available ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (in ?c ?t) (available ?h))
    :effect (and (not (in ?c ?t)) (lifting ?h ?c) (not (available ?h)))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?s ?p) (lifting ?h ?c) (clear ?s))
    :effect (and (not (lifting ?h ?c)) (on ?c ?s) (available ?h) (not (clear ?s)) (clear ?c))
  )

)