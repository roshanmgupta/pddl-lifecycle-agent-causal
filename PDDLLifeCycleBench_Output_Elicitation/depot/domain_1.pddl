(define (domain depot)
  (:requirements :strips :typing)

  (:types
    locatable place - object
    depot distributor - place
    hoist surface truck - locatable
    crate pallet - surface
  )

  (:predicates
    (at ?x - object ?loc - place)
    (clear ?x - surface)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (in ?c - crate ?t - truck)
    (on ?c1 - crate ?c2 - surface)
  )

  (:action drive_truck
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )

  (:action lift_hoist
    :parameters (?h - hoist ?c - crate ?s - surface ?loc - place)
    :precondition (and (at ?h ?loc) (available ?h) (at ?c ?loc) (on ?c ?s) (clear ?c))
    :effect (and (lifting ?h ?c) (not (at ?c ?loc)) (not (clear ?c)) (not (available ?h)) (not (on ?c ?s)) (clear ?s))
  )

  (:action drop_crate
    :parameters (?h - hoist ?c - crate ?s - surface ?loc - place)
    :precondition (and (at ?h ?loc) (at ?s ?loc) (clear ?s) (lifting ?h ?c))
    :effect (and (available ?h) (at ?c ?loc) (clear ?c) (on ?c ?s) (not (lifting ?h ?c)) (not (clear ?s)))
  )

  (:action load_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?loc - place)
    :precondition (and (at ?h ?loc) (at ?t ?loc) (lifting ?h ?c))
    :effect (and (in ?c ?t) (available ?h) (not (lifting ?h ?c)))
  )

  (:action unload_crate
    :parameters (?h - hoist ?c - crate ?t - truck ?loc - place)
    :precondition (and (at ?h ?loc) (at ?t ?loc) (available ?h) (in ?c ?t))
    :effect (and (lifting ?h ?c) (not (in ?c ?t)) (not (available ?h)))
  )

)