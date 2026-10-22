(define (domain satellite)
  (:requirements :strips :typing)

  (:types
    direction instrument mode satellite - object
  )

  (:predicates
    (on-board ?i - instrument ?s - satellite)
    (supports ?i - instrument ?m - mode)
    (pointing ?s - satellite ?d - direction)
    (power-avail ?s - satellite)
    (power-on ?i - instrument)
    (calibrated ?i - instrument)
    (have-image ?d - direction ?m - mode)
    (power-consumed ?i - instrument ?s - satellite)
  )

  (:action switch-on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-avail ?s) (not (power-on ?i)))
    :effect (and (power-on ?i) (power-consumed ?i ?s))
  )

  (:action switch-off
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-on ?i))
    :effect (and (not (power-on ?i)) (not (power-consumed ?i ?s)) (power-avail ?s))
  )

  (:action take-image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing ?s ?d))
    :effect (have-image ?d ?m)
  )

  (:action calibrate
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-avail ?s))
    :effect (calibrated ?i)
  )

)