(define (domain planetary_rover_domain)
  (:requirements :strips :typing)

  (:types
    lander rover waypoint - object
  )

  (:predicates
    (at ?r - rover ?w - waypoint)
    (lander_at ?l - lander ?w - waypoint)
    (has_soil_data ?r - rover)
    (has_rock_data ?r - rover)
    (communicated_soil ?r - rover ?l - lander)
    (communicated_rock ?r - rover ?l - lander)
    (at_lander ?l - lander ?w - waypoint)
    (can_traverse ?r - rover ?from - waypoint ?to - waypoint)
    (visible ?w - waypoint ?l - lander)
    (empty ?r - rover)
    (have_soil_analysis ?r - rover ?w - waypoint)
    (have_rock_analysis ?r - rover ?w - waypoint)
    (available ?r - rover)
    (communicated_soil_data ?w - waypoint)
    (communicated_rock_data ?w - waypoint)
  )

  (:action move
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?w - waypoint)
    :precondition (at ?r ?w)
    :effect (has_soil_data ?r)
  )

  (:action sample_rock
    :parameters (?r - rover ?w - waypoint)
    :precondition (at ?r ?w)
    :effect (has_rock_data ?r)
  )

  (:action communicate_soil
    :parameters (?r - rover ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?w) (lander_at ?l ?w) (has_soil_data ?r))
    :effect (communicated_soil ?r ?l)
  )

  (:action communicate_rock
    :parameters (?r - rover ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?w) (lander_at ?l ?w) (has_rock_data ?r))
    :effect (communicated_rock ?r ?l)
  )

)