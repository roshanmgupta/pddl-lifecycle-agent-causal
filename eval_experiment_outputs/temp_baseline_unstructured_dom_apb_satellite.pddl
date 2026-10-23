(define (domain satellite)
  (:requirements :strips)
  (:predicates
    (pointing-at ?satellite ?direction)
    (on-board ?instrument ?satellite)
    (supports ?instrument ?mode)
    (calibration-target ?instrument ?direction)
    (power-available ?satellite)
    (power-on ?instrument)
    (calibrated ?instrument)
    (has-image ?direction ?mode)
  )
  (:action turn
    :parameters (?satellite ?from ?to)
    :precondition (pointing-at ?satellite ?from)
    :effect (and
      (pointing-at ?satellite ?to)
      (not (pointing-at ?satellite ?from))
    )
  )
  (:action switch-on
    :parameters (?instrument ?satellite)
    :precondition (and (on-board ?instrument ?satellite) (power-available ?satellite))
    :effect (and
      (power-on ?instrument)
      (not (calibrated ?instrument))
      (not (power-available ?satellite))
    )
  )
  (:action switch-off
    :parameters (?instrument ?satellite)
    :precondition (and (on-board ?instrument ?satellite) (power-on ?instrument))
    :effect (and
      (not (power-on ?instrument))
      (power-available ?satellite)
    )
  )
  (:action calibrate
    :parameters (?instrument ?satellite ?direction)
    :precondition (and (on-board ?instrument ?satellite) (calibration-target ?instrument ?direction) (pointing-at ?satellite ?direction) (power-on ?instrument))
    :effect (calibrated ?instrument)
  )
  (:action take-image
    :parameters (?satellite ?direction ?instrument ?mode)
    :precondition (and (calibrated ?instrument) (on-board ?instrument ?satellite) (supports ?instrument ?mode) (power-on ?instrument) (pointing-at ?satellite ?direction))
    :effect (has-image ?direction ?mode)
  )
)