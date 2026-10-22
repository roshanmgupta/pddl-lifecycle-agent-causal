(define (domain planetary_rover_exploration)
  (:requirements :strips :typing)

  (:types
    calibration_target data instrument lander objective rover sample_store waypoint - object
    antenna camera drill spectrometer - instrument
  )

  (:predicates
    (at ?r - rover ?w - waypoint)
    (connected ?w1 - waypoint ?w2 - waypoint)
    (energy_available ?r - rover)
    (has_camera ?r - rover ?c - camera)
    (has_drill ?r - rover ?d - drill)
    (has_spectrometer ?r - rover ?s - spectrometer)
    (has_antenna ?r - rover ?a - antenna)
    (has_sample_store ?r - rover ?s - sample_store)
    (sample_store_empty ?s - sample_store)
    (sample_store_full ?s - sample_store)
    (sample_store_dirty ?s - sample_store)
    (calibration_target_visible ?t - calibration_target ?w - waypoint)
    (calibrated ?c - camera ?w - waypoint)
    (objective_at ?o - objective ?w - waypoint)
    (stored ?r - rover ?d - data)
    (transmitted ?d - data)
    (line_of_sight ?w - waypoint ?l - lander)
  )

  (:action move_rover
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (at ?r ?from) (connected ?from ?to) (energy_available ?r))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action calibrate_camera
    :parameters (?r - rover ?c - camera ?w - waypoint ?t - calibration_target)
    :precondition (and (at ?r ?w) (has_camera ?r ?c) (calibration_target_visible ?t ?w))
    :effect (calibrated ?c ?w)
  )

  (:action capture_image
    :parameters (?r - rover ?c - camera ?w - waypoint ?o - objective ?d - data)
    :precondition (and (at ?r ?w) (has_camera ?r ?c) (calibrated ?c ?w) (objective_at ?o ?w))
    :effect (stored ?r ?d)
  )

  (:action analyze_soil
    :parameters (?r - rover ?w - waypoint ?d - drill ?s - sample_store ?data - data)
    :precondition (and (at ?r ?w) (has_drill ?r ?d) (has_sample_store ?r ?s) (sample_store_empty ?s))
    :effect (and (not (sample_store_empty ?s)) (sample_store_full ?s) (sample_store_dirty ?s) (stored ?r ?data))
  )

  (:action analyze_rock
    :parameters (?r - rover ?w - waypoint ?s - spectrometer ?store - sample_store ?data - data)
    :precondition (and (at ?r ?w) (has_spectrometer ?r ?s) (has_sample_store ?r ?store) (sample_store_empty ?store))
    :effect (and (not (sample_store_empty ?store)) (sample_store_full ?store) (sample_store_dirty ?store) (stored ?r ?data))
  )

  (:action transmit_data
    :parameters (?r - rover ?w - waypoint ?l - lander ?a - antenna ?d - data)
    :precondition (and (at ?r ?w) (has_antenna ?r ?a) (stored ?r ?d) (line_of_sight ?w ?l))
    :effect (transmitted ?d)
  )

  (:action clear_data
    :parameters (?r - rover ?d - data)
    :precondition (and (stored ?r ?d) (transmitted ?d))
    :effect (not (stored ?r ?d))
  )

)