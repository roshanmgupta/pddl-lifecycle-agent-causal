(define (domain satellite)
  (:requirements :strips :typing)

  (:types
    direction instrument mode satellite - object
  )

  (:predicates
    (supports ?i - instrument ?m - mode)
    (calibration-target ?i - instrument ?d - direction)
    (on-board ?i - instrument ?s - satellite)
    (power-available ?s - satellite)
    (power-on ?i - instrument)
    (pointing-at ?s - satellite ?d - direction)
    (has-image ?d - direction ?m - mode)
    (calibrated ?i - instrument)
  )

  (:action turn-satellite
    :parameters (?s - satellite ?from - direction ?to - direction)
    :precondition (pointing-at ?s ?from)
    :effect (and (pointing-at ?s ?to) (not (pointing-at ?s ?from)))
  )

  (:action switch-on-instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-available ?s))
    :effect (and (power-on ?i) (not (calibrated ?i)) (not (power-available ?s)))
  )

  (:action switch-off-instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-on ?i))
    :effect (and (power-available ?s) (not (power-on ?i)))
  )

  (:action calibrate-instrument
    :parameters (?i - instrument ?s - satellite ?d - direction)
    :precondition (and (on-board ?i ?s) (calibration-target ?i ?d) (pointing-at ?s ?d) (power-on ?i))
    :effect (calibrated ?i)
  )

  (:action take-image
    :parameters (?s - satellite ?i - instrument ?d - direction ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing-at ?s ?d))
    :effect (has-image ?d ?m)
  )

)