(define (domain transport08-bfs)
  (:requirements :strips :typing)
  (:types
    location vehicle package capacity-number - object
  )
  (:predicates
    (at ?v - vehicle ?l - location)
    (in ?p - package ?v - vehicle)
    (at-package ?p - package ?l - location)
    (has-capacity ?v - vehicle ?c - capacity-number)
    (road ?l1 - location ?l2 - location)
    (capacity-predecessor ?c1 - capacity-number ?c2 - capacity-number)
  )
  (:action drive
    :parameters (?v - vehicle ?from - location ?to - location)
    :precondition (and (at ?v ?from) (road ?from ?to))
    :effect (and (not (at ?v ?from)) (at ?v ?to))
  )
  (:action pick-up
    :parameters (?v - vehicle ?p - package ?l - location ?e - capacity-number ?d - capacity-number)
    :precondition (and (at ?v ?l) (at-package ?p ?l) (capacity-predecessor ?d ?e) (has-capacity ?v ?e))
    :effect (and (in ?p ?v) (not (at-package ?p ?l)) (not (has-capacity ?v ?e)) (has-capacity ?v ?d))
  )
  (:action drop-off
    :parameters (?v - vehicle ?p - package ?l - location ?d - capacity-number ?e - capacity-number)
    :precondition (and (at ?v ?l) (in ?p ?v) (capacity-predecessor ?d ?e) (has-capacity ?v ?d))
    :effect (and (at-package ?p ?l) (not (in ?p ?v)) (not (has-capacity ?v ?d)) (has-capacity ?v ?e))
  )
)