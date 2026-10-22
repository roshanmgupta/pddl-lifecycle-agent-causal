(define (domain planetary_rover_domain)
  (:requirements :strips :typing)

  (:types
    lander rover waypoint - object
  )

  (:predicates
    (at ?r - rover ?w - waypoint)
    (at_lander ?l - lander ?w - waypoint)
    (soil_at ?w - waypoint)
    (rock_at ?w - waypoint)
    (has_soil_data ?r - rover)
    (has_rock_data ?r - rover)
    (communicated_soil ?r - rover ?l - lander)
    (communicated_rock ?r - rover ?l - lander)
  )

  (:action move
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?w - waypoint)
    :precondition (and (at ?r ?w) (soil_at ?w))
    :effect (has_soil_data ?r)
  )

  (:action sample_rock
    :parameters (?r - rover ?w - waypoint)
    :precondition (and (at ?r ?w) (rock_at ?w))
    :effect (has_rock_data ?r)
  )

  (:action communicate_soil
    :parameters (?r - rover ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?w) (at_lander ?l ?w) (has_soil_data ?r))
    :effect (communicated_soil ?r ?l)
  )

  (:action communicate_rock
    :parameters (?r - rover ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?w) (at_lander ?l ?w) (has_rock_data ?r))
    :effect (communicated_rock ?r ?l)
  )

)