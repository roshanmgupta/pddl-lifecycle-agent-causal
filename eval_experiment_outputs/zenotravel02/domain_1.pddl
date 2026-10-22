(define (domain zenotravel02)
  (:requirements :strips :typing)

  (:types
    aircraft city flight_level person - object
  )

  (:predicates
    (at ?a - aircraft ?c - city)
    (in ?p - person ?a - aircraft)
    (person_at ?p - person ?c - city)
    (fuel_level ?a - aircraft ?f - flight_level)
    (next ?f1 - flight_level ?f2 - flight_level)
    (is_person ?p - person)
    (is_aircraft ?a - aircraft)
    (is_city ?c - city)
    (is_flight_level ?f - flight_level)
  )

  (:action board
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (is_person ?p) (is_aircraft ?a) (is_city ?c) (person_at ?p ?c) (at ?a ?c))
    :effect (and (in ?p ?a) (not (person_at ?p ?c)))
  )

  (:action debark
    :parameters (?p - person ?a - aircraft ?c - city)
    :precondition (and (is_person ?p) (is_aircraft ?a) (is_city ?c) (in ?p ?a) (at ?a ?c))
    :effect (and (person_at ?p ?c) (not (in ?p ?a)))
  )

  (:action fly
    :parameters (?a - aircraft ?from - city ?to - city ?f1 - flight_level ?f2 - flight_level)
    :precondition (and (is_aircraft ?a) (is_city ?from) (is_city ?to) (is_flight_level ?f1) (is_flight_level ?f2) (at ?a ?from) (fuel_level ?a ?f1) (next ?f1 ?f2))
    :effect (and (at ?a ?to) (fuel_level ?a ?f2) (not (at ?a ?from)) (not (fuel_level ?a ?f1)))
  )

  (:action zoom
    :parameters (?a - aircraft ?from - city ?to - city ?f1 - flight_level ?f2 - flight_level ?f3 - flight_level)
    :precondition (and (is_aircraft ?a) (is_city ?from) (is_city ?to) (is_flight_level ?f1) (is_flight_level ?f2) (is_flight_level ?f3) (at ?a ?from) (fuel_level ?a ?f1) (next ?f1 ?f2) (next ?f2 ?f3))
    :effect (and (at ?a ?to) (fuel_level ?a ?f3) (not (at ?a ?from)) (not (fuel_level ?a ?f1)))
  )

  (:action refuel
    :parameters (?a - aircraft ?c - city ?f1 - flight_level ?f2 - flight_level)
    :precondition (and (is_aircraft ?a) (is_city ?c) (is_flight_level ?f1) (is_flight_level ?f2) (fuel_level ?a ?f1) (next ?f2 ?f1) (at ?a ?c))
    :effect (and (fuel_level ?a ?f2) (not (fuel_level ?a ?f1)))
  )

)