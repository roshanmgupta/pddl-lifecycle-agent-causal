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
  )

  (:action turn_to
    :parameters (?s - satellite ?d_new - direction ?d_prev - direction)
    :precondition (pointing ?s ?d_prev)
    :effect (and (pointing ?s ?d_new) (not (pointing ?s ?d_prev)))
  )

  (:action switch_on
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-avail ?s))
    :effect (and (power-on ?i) (not (power-avail ?s)) (not (calibrated ?i)))
  )

  (:action calibrate
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on-board ?i ?s) (power-on ?i))
    :effect (calibrated ?i)
  )

  (:action take_image
    :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
    :precondition (and (calibrated ?i) (on-board ?i ?s) (supports ?i ?m) (power-on ?i) (pointing ?s ?d))
    :effect (have-image ?d ?m)
  )

)