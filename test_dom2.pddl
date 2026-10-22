(define (domain depot)
  (:requirements :strips :typing)

  (:types
    depot distributor - place
    locatable place surface - object
    hoist truck - locatable
    crate pallet - surface
  )

  (:predicates
    (at ?x - object ?y - object)
    (clear ?x - surface)
    (available ?x - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
  )

  (:action drive_truck
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )

  (:action lift_crate
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?c ?p) (clear ?c) (on ?c ?s))
    :effect (and (lifting ?h ?c) (not (at ?c ?p)) (not (available ?h)) (not (on ?c ?s)) (clear ?c) (on ?c ?s))
  )

  (:action drop_crate
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (lifting ?h ?c) (clear ?c) (on ?c ?s))
    :effect (and (at ?c ?p) (clear ?c) (on ?c ?s) (available ?h) (not (lifting ?h ?c)))
  )

  (:action load_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (lifting ?h ?c))
    :effect (and (in ?c ?t) (available ?h) (not (lifting ?h ?c)))
  )

  (:action unload_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?p - place)
    :precondition (and (at ?h ?p) (at ?t ?p) (available ?h) (in ?c ?t))
    :effect (and (lifting ?h ?c) (not (in ?c ?t)) (not (available ?h)))
  )

)