(define (domain ferry_scaled)
  (:requirements :strips :typing)

  (:types
    car location - object
  )

  (:predicates
    (at-ferry ?l - location)
    (empty-ferry)
    (on ?c - car)
    (at ?c - car ?l - location)
    (not-equal ?l1 - location ?l2 - location)
  )

  (:action sail
    :parameters (?from - location ?to - location)
    :precondition (and (not-equal ?from ?to) (at-ferry ?from))
    :effect (and (not (at-ferry ?from)) (at-ferry ?to))
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