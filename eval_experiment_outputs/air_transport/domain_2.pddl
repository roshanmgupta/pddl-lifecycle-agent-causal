(define (domain air_transport)
  (:requirements :strips :typing)

  (:types
    aircraft city fuel_level passenger - object
  )

  (:predicates
    (at ?a - aircraft ?c - city)
    (on_board ?p - passenger ?a - aircraft)
    (in_city ?p - passenger ?c - city)
    (target_city ?p - passenger ?c - city)
    (has_fuel ?a - aircraft ?f - fuel_level)
    (can_fly_normal ?a - aircraft)
    (can_fly_zoom ?a - aircraft)
  )

  (:action fly_normal
    :parameters (?a - aircraft ?from - city ?to - city ?f - fuel_level)
    :precondition (and (at ?a ?from) (has_fuel ?a ?f) (can_fly_normal ?a))
    :effect (and (not (at ?a ?from)) (at ?a ?to) (not (has_fuel ?a ?f)))
  )

  (:action fly_zoom
    :parameters (?a - aircraft ?from - city ?to - city ?f - fuel_level)
    :precondition (and (at ?a ?from) (has_fuel ?a ?f) (can_fly_zoom ?a))
    :effect (and (not (at ?a ?from)) (at ?a ?to) (not (has_fuel ?a ?f)))
  )

  (:action board
    :parameters (?p - passenger ?a - aircraft ?c - city)
    :precondition (and (at ?a ?c) (in_city ?p ?c))
    :effect (and (not (in_city ?p ?c)) (on_board ?p ?a))
  )

  (:action debark
    :parameters (?p - passenger ?a - aircraft ?c - city)
    :precondition (and (at ?a ?c) (on_board ?p ?a))
    :effect (and (not (on_board ?p ?a)) (in_city ?p ?c))
  )

  (:action refuel
    :parameters (?a - aircraft ?c - city ?f - fuel_level)
    :precondition (at ?a ?c)
    :effect (has_fuel ?a ?f)
  )

)