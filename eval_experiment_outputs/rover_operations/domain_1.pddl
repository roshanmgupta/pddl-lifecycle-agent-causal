(define (domain rover_operations)
  (:requirements :strips :typing)

  (:types
    camera lander mode object objective rover store waypoint - object
  )

  (:predicates
    (can_traverse ?r - rover ?from - waypoint ?to - waypoint)
    (available ?r - rover)
    (at ?r - rover ?w - waypoint)
    (visible ?w1 - waypoint ?w2 - waypoint)
    (at_soil_sample ?w - waypoint)
    (equipped_for_soil_analysis ?r - rover)
    (store_of ?s - store ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (at_rock_sample ?w - waypoint)
    (equipped_for_rock_analysis ?r - rover)
    (equipped_for_imaging ?r - rover)
    (calibration_target ?c - camera ?o - objective)
    (on_board ?c - camera ?r - rover)
    (calibrated ?c - camera ?r - rover)
    (supports ?c - camera ?m - mode)
    (has_soil_analysis ?r - rover ?w - waypoint)
    (has_rock_analysis ?r - rover ?w - waypoint)
    (has_image ?r - rover ?o - objective ?m - mode)
    (at_lander ?l - lander ?w - waypoint)
    (channel_free ?l - lander)
    (communicated_soil_data ?w - waypoint)
    (communicated_rock_data ?w - waypoint)
    (communicated_image_data ?o - objective ?m - mode)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (can_traverse ?r ?from ?to) (available ?r) (at ?r ?from) (visible ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (at_soil_sample ?w) (equipped_for_soil_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_soil_analysis ?r ?w) (not (empty ?s)) (not (at_soil_sample ?w)))
  )

  (:action sample_rock
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (at_rock_sample ?w) (equipped_for_rock_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_rock_analysis ?r ?w) (not (empty ?s)) (not (at_rock_sample ?w)))
  )

  (:action drop
    :parameters (?r - rover ?s - store)
    :precondition (and (store_of ?s ?r) (full ?s))
    :effect (and (empty ?s) (not (full ?s)))
  )

  (:action calibrate
    :parameters (?r - rover ?c - camera ?o - objective ?w - waypoint)
    :precondition (and (equipped_for_imaging ?r) (calibration_target ?c ?o) (at ?r ?w) (on_board ?c ?r))
    :effect (calibrated ?c ?r)
  )

  (:action take_image
    :parameters (?r - rover ?w - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (calibrated ?c ?r) (on_board ?c ?r) (equipped_for_imaging ?r) (supports ?c ?m) (at ?r ?w))
    :effect (and (has_image ?r ?o ?m) (not (calibrated ?c ?r)))
  )

  (:action communicate_soil_data
    :parameters (?r - rover ?w1 - waypoint ?l - lander ?w2 - waypoint ?w3 - waypoint)
    :precondition (and (at ?r ?w1) (at_lander ?l ?w2) (has_soil_analysis ?r ?w3) (visible ?w1 ?w2) (available ?r) (channel_free ?l))
    :effect (and (channel_free ?l) (communicated_soil_data ?w3) (available ?r) (not (available ?r)) (not (channel_free ?l)))
  )

  (:action communicate_rock_data
    :parameters (?r - rover ?w1 - waypoint ?l - lander ?w2 - waypoint ?w3 - waypoint)
    :precondition (and (at ?r ?w1) (at_lander ?l ?w2) (has_rock_analysis ?r ?w3) (visible ?w1 ?w2) (available ?r) (channel_free ?l))
    :effect (and (channel_free ?l) (communicated_rock_data ?w3) (available ?r) (not (available ?r)) (not (channel_free ?l)))
  )

  (:action communicate_image_data
    :parameters (?r - rover ?w1 - waypoint ?l - lander ?w2 - waypoint ?o - objective ?m - mode)
    :precondition (and (at ?r ?w1) (at_lander ?l ?w2) (has_image ?r ?o ?m) (visible ?w1 ?w2) (available ?r) (channel_free ?l))
    :effect (and (channel_free ?l) (communicated_image_data ?o ?m) (available ?r) (not (available ?r)) (not (channel_free ?l)))
  )

)