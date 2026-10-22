(define (domain satellite)
  (:requirements :strips :typing)

  (:types
    direction instrument mode satellite - object
  )

  (:predicates
    (pointing_at ?s - satellite ?d - direction)
    (on_board ?i - instrument ?s - satellite)
    (power_available ?s - satellite)
    (power_on ?i - instrument)
    (calibrated ?i - instrument)
    (supports ?i - instrument ?m - mode)
    (calibration_target ?i - instrument ?d - direction)
    (has_image ?d - direction ?m - mode)
    (transmitted_image ?d - direction ?m - mode)
    (have-image ?d - direction ?m - mode)
    (pointing ?s - satellite ?d - direction)
  )

  (:action turn_satellite
    :parameters (?s - satellite ?from - direction ?to - direction)
    :precondition (pointing_at ?s ?from)
    :effect (and (not (pointing_at ?s ?from)) (pointing_at ?s ?to))
  )

  (:action switch_on_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_available ?s))
    :effect (and (power_on ?i) (not (calibrated ?i)) (not (power_available ?s)))
  )

  (:action switch_off_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_on ?i))
    :effect (and (power_available ?s) (not (power_on ?i)))
  )

  (:action calibrate_instrument
    :parameters (?i - instrument ?s - satellite ?d - direction)
    :precondition (and (on_board ?i ?s) (calibration_target ?i ?d) (pointing_at ?s ?d) (power_on ?i))
    :effect (calibrated ?i)
  )

  (:action take_image
    :parameters (?d - direction ?i - instrument ?m - mode ?s - satellite)
    :precondition (and (calibrated ?i) (on_board ?i ?s) (supports ?i ?m) (power_on ?i) (pointing_at ?s ?d))
    :effect (has_image ?d ?m)
  )

  (:action transmit_image
    :parameters (?d - direction ?m - mode ?s - satellite)
    :precondition (and (has_image ?d ?m) (power_available ?s))
    :effect (transmitted_image ?d ?m)
  )

)