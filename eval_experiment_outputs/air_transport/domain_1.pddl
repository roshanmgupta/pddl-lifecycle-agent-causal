(define (domain air_transport)
  (:requirements :strips :typing)

  (:types
    aircraft city fuel_level passenger speed_mode - object
  )

  (:predicates
    (at_aircraft ?a - aircraft ?c - city)
    (at_passenger ?p - passenger ?c - city)
    (in_aircraft ?p - passenger ?a - aircraft)
    (current_fuel ?a - aircraft ?f - fuel_level)
    (current_speed ?a - aircraft ?s - speed_mode)
    (can_refuel ?a - aircraft ?c - city)
  )

  (:action fly_normal
    :parameters (?a - aircraft ?from - city ?to - city ?f - fuel_level ?s - speed_mode)
    :precondition (and (at_aircraft ?a ?from) (current_fuel ?a ?f) (current_speed ?a ?s) (= ?s normal))
    :effect (and (not (at_aircraft ?a ?from)) (at_aircraft ?a ?to))
  )

  (:action fly_zoom
    :parameters (?a - aircraft ?from - city ?to - city ?f - fuel_level ?s - speed_mode)
    :precondition (and (at_aircraft ?a ?from) (current_fuel ?a ?f) (current_speed ?a ?s) (= ?s zoom))
    :effect (and (not (at_aircraft ?a ?from)) (at_aircraft ?a ?to))
  )

  (:action board
    :parameters (?p - passenger ?a - aircraft ?c - city)
    :precondition (and (at_passenger ?p ?c) (at_aircraft ?a ?c))
    :effect (and (not (at_passenger ?p ?c)) (in_aircraft ?p ?a))
  )

  (:action debark
    :parameters (?p - passenger ?a - aircraft ?c - city)
    :precondition (and (in_aircraft ?p ?a) (at_aircraft ?a ?c))
    :effect (and (not (in_aircraft ?p ?a)) (at_passenger ?p ?c))
  )

  (:action refuel
    :parameters (?a - aircraft ?c - city ?f - fuel_level)
    :precondition (and (at_aircraft ?a ?c) (can_refuel ?a ?c))
    :effect (current_fuel ?a ?f)
  )

  (:action change_speed
    :parameters (?a - aircraft ?old_s - speed_mode ?new_s - speed_mode)
    :precondition (current_speed ?a ?old_s)
    :effect (and (not (current_speed ?a ?old_s)) (current_speed ?a ?new_s))
  )

)