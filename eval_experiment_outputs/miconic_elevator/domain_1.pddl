(define (domain miconic_elevator)
  (:requirements :strips :typing)

  (:types
    floor passenger - object
  )

  (:predicates
    (directly_below ?lower - floor ?upper - floor)
    (lift_at ?f - floor)
    (origin ?p - passenger ?f - floor)
    (destination ?p - passenger ?f - floor)
    (boarded ?p - passenger)
    (served ?p - passenger)
  )

  (:action move_up
    :parameters (?from - floor ?to - floor)
    :precondition (and (lift_at ?from) (directly_below ?from ?to))
    :effect (and (not (lift_at ?from)) (lift_at ?to))
  )

  (:action move_down
    :parameters (?from - floor ?to - floor)
    :precondition (and (lift_at ?from) (directly_below ?to ?from))
    :effect (and (not (lift_at ?from)) (lift_at ?to))
  )

  (:action board
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift_at ?f) (origin ?p ?f))
    :effect (boarded ?p)
  )

  (:action depart
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift_at ?f) (destination ?p ?f) (boarded ?p))
    :effect (and (not (boarded ?p)) (served ?p))
  )

)