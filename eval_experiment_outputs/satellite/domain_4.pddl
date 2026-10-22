(define (domain satellite)
  (:requirements :strips :typing)

  (:types
    direction instrument mode satellite - object
  )

  (:predicates
    (pointing ?s - satellite ?d - direction)
    (on_board ?i - instrument ?s - satellite)
    (power_available ?s - satellite)
    (power_on ?i - instrument)
    (calibration_target ?i - instrument ?d - direction)
    (supports ?i - instrument ?m - mode)
    (calibrated ?i - instrument)
    (has_image ?d - direction ?m - mode)
  )

  (:action turn_satellite
    :parameters (?s - satellite ?from - direction ?to - direction)
    :precondition (pointing ?s ?from)
    :effect (and (not (pointing ?s ?from)) (pointing ?s ?to))
  )

  (:action switch_on_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_available ?s))
    :effect (and (power_on ?i) (not (power_available ?s)) (not (calibrated ?i)))
  )

  (:action switch_off_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_board ?i ?s) (power_on ?i))
    :effect (and (not (power_on ?i)) (power_available ?s))
  )

  (:action calibrate_instrument
    :parameters (?i - instrument ?s - satellite ?d - direction)
    :precondition (and (on_board ?i ?s) (calibration_target ?i ?d) (pointing ?s ?d) (power_on ?i))
    :effect (calibrated ?i)
  )

  (:action take_image
    :parameters (?d - direction ?i - instrument ?m - mode ?s - satellite)
    :precondition (and (calibrated ?i) (on_board ?i ?s) (supports ?i ?m) (power_on ?i) (pointing ?s ?d))
    :effect (has_image ?d ?m)
  )

)