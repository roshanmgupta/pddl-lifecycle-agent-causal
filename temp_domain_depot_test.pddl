(define (domain depot)
  (:requirements :strips :typing)

  (:types
    locatable place - object
    depot distributor - place
    hoist surface truck - locatable
    crate pallet - surface
  )

  (:predicates
    (at ?x - locatable ?p - place)
    (clear ?x - surface)
    (available ?h - hoist)
    (lifting ?h - hoist ?c - crate)
    (on ?c - crate ?s - surface)
    (in ?c - crate ?t - truck)
  )

  (:action drive_truck
    :parameters (?t - truck ?from - place ?to - place)
    :precondition (at ?t ?from)
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )

  (:action lift_hoist
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (available ?h) (at ?c ?p) (on ?c ?s) (clear ?c))
    :effect (and (lifting ?h ?c) (clear ?s) (not (at ?c ?p)) (not (clear ?c)) (not (available ?h)) (not (on ?c ?s)))
  )

  (:action drop_crate
    :parameters (?h - hoist ?c - crate ?s - surface ?p - place)
    :precondition (and (at ?h ?p) (at ?s ?p) (clear ?s) (lifting ?h ?c))
    :effect (and (at ?c ?p) (clear ?c) (on ?c ?s) (available ?h) (not (lifting ?h ?c)) (not (clear ?s)))
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