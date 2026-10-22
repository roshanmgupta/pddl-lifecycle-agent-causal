(define (domain depots_domain)
  (:requirements :strips :typing)

  (:types
    crate depot distributor hoist pallet truck - object
  )

  (:predicates
    (at ?h - hoist ?d - depot)
    (on ?c - crate ?p - pallet)
    (on ?c - crate ?c2 - crate)
    (at ?t - truck ?d - depot)
    (at ?t - truck ?d - distributor)
    (loaded ?t - truck ?c - crate)
    (empty ?t - truck)
    (holding ?h - hoist ?c - crate)
    (clear ?h - hoist)
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?d - depot)
    :precondition (and (at ?h ?d) (at ?t ?d) (holding ?h ?c))
    :effect (and (not (holding ?h ?c)) (loaded ?t ?c) (clear ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?d - depot)
    :precondition (and (at ?h ?d) (at ?t ?d) (loaded ?t ?c) (clear ?h))
    :effect (and (not (loaded ?t ?c)) (holding ?h ?c) (empty ?t))
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?p - pallet ?d - depot)
    :precondition (and (at ?h ?d) (on ?c ?p) (clear ?h))
    :effect (and (not (on ?c ?p)) (holding ?h ?c))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?p - pallet ?d - depot)
    :precondition (and (at ?h ?d) (holding ?h ?c))
    :effect (and (not (holding ?h ?c)) (on ?c ?p) (clear ?h))
  )

)