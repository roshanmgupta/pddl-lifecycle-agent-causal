(define (domain miconic_elevator_luggage)
  (:requirements :strips :typing)

  (:types
    floor luggage passenger - object
  )

  (:predicates
    (origin ?p - passenger ?f - floor)
    (destin ?p - passenger ?f - floor)
    (above ?f1 - floor ?f2 - floor)
    (boarded ?p - passenger)
    (served ?p - passenger)
    (lift-at ?f - floor)
    (passenger-at ?p - passenger ?f - floor)
    (luggage-at ?lug - luggage ?f - floor)
    (luggage-in ?lug - luggage)
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

  (:action board_passenger
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift-at ?f) (passenger-at ?p ?f) (origin ?p ?f))
    :effect (and (not (passenger-at ?p ?f)) (boarded ?p))
  )

  (:action depart_passenger
    :parameters (?p - passenger ?f - floor)
    :precondition (and (lift-at ?f) (boarded ?p) (destin ?p ?f))
    :effect (and (not (boarded ?p)) (served ?p))
  )

  (:action load_luggage
    :parameters (?lug - luggage ?f - floor)
    :precondition (and (lift-at ?f) (luggage-at ?lug ?f))
    :effect (and (not (luggage-at ?lug ?f)) (luggage-in ?lug))
  )

  (:action unload_luggage
    :parameters (?lug - luggage ?f - floor)
    :precondition (and (lift-at ?f) (luggage-in ?lug))
    :effect (and (not (luggage-in ?lug)) (luggage-at ?lug ?f))
  )

)