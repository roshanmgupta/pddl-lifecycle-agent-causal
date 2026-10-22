(define (domain depot_planbench)
  (:requirements :strips :typing)

  (:types
    hoist place surface truck - object
    depot distributor - place
    crate pallet - surface
  )

  (:predicates
    (at ?x - truck ?y - place)
    (at ?x - surface ?y - place)
    (at ?x - hoist ?y - place)
    (clear ?x - surface)
    (available ?x - hoist)
    (lifting ?x - hoist ?y - crate)
    (on ?x - crate ?y - surface)
    (in ?x - crate ?y - truck)
  )

  (:action drive
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?c ?p) (on ?c ?s) (clear ?c) (available ?h))
    :effect (and (not (at ?c ?p)) (not (on ?c ?s)) (not (clear ?c)) (clear ?s) (not (available ?h)) (lifting ?h ?c))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?s ?p) (clear ?s) (lifting ?h ?c))
    :effect (and (available ?h) (not (lifting ?h ?c)) (at ?c ?p) (not (clear ?s)) (clear ?c) (on ?c ?s))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (lifting ?h ?c))
    :effect (and (not (lifting ?h ?c)) (in ?c ?t) (available ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (available ?h) (in ?c ?t))
    :effect (and (not (available ?h)) (lifting ?h ?c) (not (in ?c ?t)))
  )

)