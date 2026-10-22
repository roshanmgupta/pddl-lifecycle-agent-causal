(define (domain depot_logistics)
  (:requirements :strips :typing)

  (:types
    crate depot hoist pallet vehicle - object
  )

  (:predicates
    (at ?v - vehicle ?d - depot)
    (at_hoist ?h - hoist ?d - depot)
    (on_crate ?c - crate ?p - pallet)
    (on_pallet ?p - pallet ?d - depot)
    (holding ?h - hoist ?c - crate)
    (in_truck ?c - crate ?t - vehicle)
  )

  (:action load_hoist
    :parameters (?h - hoist ?c - crate ?p - pallet ?d - depot)
    :precondition (and (at_hoist ?h ?d) (on_crate ?c ?p) (on_pallet ?p ?d) (not (holding ?h ?c)))
    :effect (and (holding ?h ?c) (not (on_crate ?c ?p)))
  )

  (:action load_truck
    :parameters (?h - hoist ?c - crate ?t - vehicle ?d - depot)
    :precondition (and (holding ?h ?c) (at_hoist ?h ?d) (at ?t ?d) (not (in_truck ?c ?t)))
    :effect (and (not (holding ?h ?c)) (in_truck ?c ?t))
  )

  (:action move_hoist
    :parameters (?h - hoist ?d1 - depot ?d2 - depot)
    :precondition (and (at_hoist ?h ?d1) (not (at_hoist ?h ?d2)))
    :effect (and (not (at_hoist ?h ?d1)) (at_hoist ?h ?d2))
  )

)