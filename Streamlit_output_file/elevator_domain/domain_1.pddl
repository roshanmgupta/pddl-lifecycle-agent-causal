(define (domain elevator_domain)
  (:requirements :strips :typing)

  (:types
    elevator floor passenger - object
  )

  (:predicates
    (lift-at ?e - elevator ?f - floor)
    (at ?p - passenger ?f - floor)
    (boarded ?p - passenger ?e - elevator)
  )

  (:action move
    :parameters (?e - elevator ?from - floor ?to - floor)
    :precondition (lift-at ?e ?from)
    :effect (and (not (lift-at ?e ?from)) (lift-at ?e ?to))
  )

  (:action board
    :parameters (?p - passenger ?e - elevator ?f - floor)
    :precondition (and (lift-at ?e ?f) (at ?p ?f))
    :effect (and (not (at ?p ?f)) (boarded ?p ?e))
  )

  (:action leave
    :parameters (?p - passenger ?e - elevator ?f - floor)
    :precondition (and (lift-at ?e ?f) (boarded ?p ?e))
    :effect (and (not (boarded ?p ?e)) (at ?p ?f))
  )

)