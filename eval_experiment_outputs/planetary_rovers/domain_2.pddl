(define (domain planetary_rovers)
  (:requirements :strips :typing)

  (:types
    camera lander mode rover store visible_object - object
    objective waypoint - visible_object
  )

  (:predicates
    (at ?r - rover ?w - waypoint)
    (can_traverse ?r - rover ?from - waypoint ?to - waypoint)
    (available ?r - rover)
    (visible ?from - visible_object ?to - visible_object)
    (soil_sample_at ?w - waypoint)
    (rock_sample_at ?w - waypoint)
    (equipped_for_soil_analysis ?r - rover)
    (equipped_for_rock_analysis ?r - rover)
    (store_of ?s - store ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (has_soil_analysis ?r - rover ?w - waypoint)
    (has_rock_analysis ?r - rover ?w - waypoint)
    (equipped_for_imaging ?r - rover)
    (calibration_target ?c - camera ?o - objective)
    (on_board ?c - camera ?r - rover)
    (calibrated_to ?c - camera ?r - rover)
    (supports ?c - camera ?m - mode)
    (has_image ?r - rover ?o - objective ?m - mode)
    (channel_free ?l - lander)
    (communicated_soil_data ?w - waypoint)
    (communicated_rock_data ?w - waypoint)
    (communicated_image_data ?o - objective ?m - mode)
    (lander_at ?l - lander ?w - waypoint)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (can_traverse ?r ?from ?to) (available ?r) (at ?r ?from) (visible ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action sample_soil
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (soil_sample_at ?w) (equipped_for_soil_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_soil_analysis ?r ?w) (not (empty ?s)) (not (soil_sample_at ?w)))
  )

  (:action sample_rock
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (rock_sample_at ?w) (equipped_for_rock_analysis ?r) (store_of ?s ?r) (empty ?s))
    :effect (and (full ?s) (has_rock_analysis ?r ?w) (not (empty ?s)) (not (rock_sample_at ?w)))
  )

  (:action drop_contents
    :parameters (?r - rover ?s - store)
    :precondition (and (store_of ?s ?r) (full ?s))
    :effect (and (empty ?s) (not (full ?s)))
  )

  (:action calibrate
    :parameters (?r - rover ?c - camera ?o - objective ?w - waypoint)
    :precondition (and (equipped_for_imaging ?r) (calibration_target ?c ?o) (at ?r ?w) (visible ?o ?w) (on_board ?c ?r))
    :effect (calibrated_to ?c ?r)
  )

  (:action take_image
    :parameters (?r - rover ?w - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (calibrated_to ?c ?r) (on_board ?c ?r) (equipped_for_imaging ?r) (supports ?c ?m) (visible ?o ?w) (at ?r ?w))
    :effect (and (has_image ?r ?o ?m) (not (calibrated_to ?c ?r)) (on_board ?c ?r))
  )

  (:action communicate_soil_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?d - waypoint)
    :precondition (and (at ?r ?w) (lander_at ?l ?d) (has_soil_analysis ?r ?d) (visible ?w ?d) (available ?r) (channel_free ?l))
    :effect (and (communicated_soil_data ?d) (available ?r) (channel_free ?l))
  )

  (:action communicate_rock_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?d - waypoint)
    :precondition (and (at ?r ?w) (lander_at ?l ?d) (has_rock_analysis ?r ?d) (visible ?w ?d) (available ?r) (channel_free ?l))
    :effect (and (communicated_rock_data ?d) (available ?r) (channel_free ?l))
  )

  (:action communicate_image_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?o - objective ?m - mode)
    :precondition (and (at ?r ?w) (lander_at ?l ?w) (has_image ?r ?o ?m) (visible ?w ?w) (available ?r) (channel_free ?l))
    :effect (and (communicated_image_data ?o ?m) (available ?r) (channel_free ?l))
  )

)