(define (domain planetary_rovers)
  (:requirements :strips :typing)

  (:types
    lander rover - rover_or_lander
    objective waypoint - waypoint_or_objective
    camera entity mode store - object
    rover_or_lander waypoint_or_objective - entity
  )

  (:predicates
    (at ?r - rover_or_lander ?w - waypoint)
    (can_traverse ?r - rover ?from - waypoint ?to - waypoint)
    (available ?r - rover)
    (visible ?from - waypoint_or_objective ?to - waypoint_or_objective)
    (equipped_for_soil_analysis ?r - rover)
    (equipped_for_rock_analysis ?r - rover)
    (store_of ?s - store ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (has_soil_analysis ?r - rover ?w - waypoint)
    (has_rock_analysis ?r - rover ?w - waypoint)
    (calibrated_to ?c - camera ?r - rover)
    (on_board ?c - camera ?r - rover)
    (supports ?c - camera ?m - mode)
    (has_image ?r - rover ?o - objective ?m - mode)
    (channel_free ?l - lander)
    (communicated_soil_data ?w - waypoint)
    (communicated_rock_data ?w - waypoint)
    (communicated_image_data ?o - objective ?m - mode)
    (equipped_for_imaging ?r - rover)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (can_traverse ?r ?from ?to) (available ?r) (at ?r ?from) (visible ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (equipped_for_soil_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_soil_analysis ?r ?w) (not (empty ?s)))
  )

  (:action sample_rock
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (equipped_for_rock_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_rock_analysis ?r ?w) (not (empty ?s)))
  )

  (:action drop_contents
    :parameters (?r - rover ?s - store)
    :precondition (and (store_of ?s ?r) (full ?s))
    :effect (and (empty ?s) (not (full ?s)))
  )

  (:action calibrate
    :parameters (?r - rover ?c - camera ?o - objective ?w - waypoint)
    :precondition (and (equipped_for_imaging ?r) (on_board ?c ?r) (at ?r ?w) (visible ?w ?o))
    :effect (calibrated_to ?c ?r)
  )

  (:action take_image
    :parameters (?r - rover ?w - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (calibrated_to ?c ?r) (on_board ?c ?r) (equipped_for_imaging ?r) (supports ?c ?m) (visible ?w ?o) (at ?r ?w))
    :effect (and (has_image ?r ?o ?m) (not (calibrated_to ?c ?r)) (on_board ?c ?r))
  )

  (:action communicate_soil_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?d - waypoint)
    :precondition (and (at ?r ?w) (at ?l ?d) (has_soil_analysis ?r ?d) (visible ?w ?d) (available ?r) (channel_free ?l))
    :effect (and (communicated_soil_data ?d) (not (available ?r)) (not (channel_free ?l)))
  )

  (:action communicate_rock_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?d - waypoint)
    :precondition (and (at ?r ?w) (at ?l ?d) (has_rock_analysis ?r ?d) (visible ?w ?d) (available ?r) (channel_free ?l))
    :effect (and (communicated_rock_data ?d) (not (available ?r)) (not (channel_free ?l)))
  )

  (:action communicate_image_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?o - objective ?m - mode)
    :precondition (and (at ?r ?w) (at ?l ?w) (has_image ?r ?o ?m) (visible ?w ?w) (available ?r) (channel_free ?l))
    :effect (and (communicated_image_data ?o ?m) (not (available ?r)) (not (channel_free ?l)))
  )

)