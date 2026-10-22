(define (domain freight_logistics)
  (:requirements :strips :typing)

  (:types
    cargo depot hoist pallet truck - object
  )

  (:predicates
    (at ?t - truck ?d - depot)
    (carrying ?t - truck ?c - cargo)
    (urgent ?c - cargo)
    (on ?c - cargo ?p - pallet)
    (on ?c1 - cargo ?c2 - cargo)
    (in ?c - cargo ?t - truck)
    (lifting ?h - hoist ?c - cargo)
    (available ?h - hoist)
    (clear ?p - pallet)
    (stacked ?c1 - cargo ?c2 - cargo)
  )

  (:action express-transit
    :parameters (?t - truck ?src - depot ?dst - depot ?c - cargo)
    :precondition (and (at ?t ?src) (carrying ?t ?c) (urgent ?c))
    :effect (and (not (at ?t ?src)) (at ?t ?dst))
  )

)