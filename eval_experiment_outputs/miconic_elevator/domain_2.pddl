(define (domain miconic_elevator)
  (:requirements :strips :typing)

  (:types
    floor passenger - object
  )

  (:predicates
    (above ?higher - floor ?lower - floor)
    (lift-at ?f - floor)
    (origin ?p - passenger ?f - floor)
    (destin ?p - passenger ?f - floor)
    (boarded ?p - passenger)
    (served ?p - passenger)
  )

  (:action move_up
    :parameters (?from - floor ?to - floor)
    :precondition (and (lift-at ?from) (above ?to ?from))
    :effect (and (not (lift-at ?from)) (lift-at ?to))
  )

  (:action move_down
    :parameters (?from - floor ?to - floor)
    :precondition (and (lift-at ?from) (above ?from ?to))
    :effect (and (not (lift-at ?from)) (lift-at ?to))
  )

  (:action board
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift-at ?f) (origin ?p ?f))
    :effect (boarded ?p)
  )

  (:action depart
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift-at ?f) (destin ?p ?f) (boarded ?p))
    :effect (and (not (boarded ?p)) (served ?p))
  )

)