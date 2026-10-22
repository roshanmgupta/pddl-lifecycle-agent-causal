(define (domain ferry)
  (:requirements :strips :typing)

  (:types
    car location - object
  )

  (:predicates
    (at-ferry ?l - location)
    (at ?c - car ?l - location)
    (on ?c - car)
    (ferry-empty)
    (not-equal ?l1 - location ?l2 - location)
  )

  (:action sail
    :parameters (?from - location ?to - location)
    :precondition (and (not-equal ?from ?to) (at-ferry ?from))
    :effect (and (not (at-ferry ?from)) (at-ferry ?to))
  )

  (:action board
    :parameters (?c - car ?l - location)
    :precondition (and (at ?c ?l) (at-ferry ?l) (ferry-empty))
    :effect (and (not (at ?c ?l)) (on ?c) (not (ferry-empty)))
  )

  (:action debark
    :parameters (?c - car ?l - location)
    :precondition (and (on ?c) (at-ferry ?l))
    :effect (and (at ?c ?l) (not (on ?c)) (ferry-empty))
  )

)