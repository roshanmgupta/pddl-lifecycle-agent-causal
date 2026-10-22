(define (domain ferry-templates)
  (:requirements :strips :typing)

  (:types
    car location - object
  )

  (:predicates
    (not-eq ?x - location ?y - location)
    (at-ferry ?l - location)
    (at ?c - car ?l - location)
    (on ?c - car)
    (empty-ferry)
  )

  (:action sail
    :parameters (?a - location ?b - location)
    :precondition (and (not-eq ?a ?b) (at-ferry ?a))
    :effect (and (at-ferry ?b) (not (at-ferry ?a)))
  )

  (:action board
    :parameters (?c - car ?l - location)
    :precondition (and (at ?c ?l) (at-ferry ?l) (empty-ferry))
    :effect (and (on ?c) (not (at ?c ?l)) (not (empty-ferry)))
  )

  (:action debark
    :parameters (?c - car ?l - location)
    :precondition (and (on ?c) (at-ferry ?l))
    :effect (and (at ?c ?l) (empty-ferry) (not (on ?c)))
  )

)