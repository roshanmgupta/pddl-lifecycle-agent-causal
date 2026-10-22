(define (domain earth_observation)
  (:requirements :strips :typing)

  (:types
    instrument mode power_level satellite target - object
  )

  (:predicates
    (onboard ?i - instrument ?s - satellite)
    (supports ?i - instrument ?m - mode)
    (powered_on ?i - instrument)
    (calibrated ?i - instrument ?t - target)
    (pointing ?s - satellite ?t - target)
    (has_image ?t - target ?m - mode)
    (power_available ?s - satellite ?p - power_level)
  )

  (:action turn_satellite
    :parameters (?s - satellite ?from - target ?to - target)
    :precondition (pointing ?s ?from)
    :effect (and (not (pointing ?s ?from)) (pointing ?s ?to))
  )

  (:action calibrate_instrument
    :parameters (?i - instrument ?s - satellite ?t - target ?m - mode)
    :precondition (and (onboard ?i ?s) (supports ?i ?m) (powered_on ?i) (pointing ?s ?t))
    :effect (calibrated ?i ?t)
  )

  (:action capture_image
    :parameters (?i - instrument ?s - satellite ?t - target ?m - mode ?p - power_level)
    :precondition (and (onboard ?i ?s) (supports ?i ?m) (powered_on ?i) (calibrated ?i ?t) (pointing ?s ?t) (power_available ?s ?p))
    :effect (and (has_image ?t ?m) (not (power_available ?s ?p)) (power_available ?s medium))
  )

  (:action power_on_instrument
    :parameters (?i - instrument ?s - satellite ?p - power_level)
    :precondition (and (onboard ?i ?s) (power_available ?s ?p))
    :effect (and (powered_on ?i) (not (power_available ?s ?p)) (power_available ?s medium))
  )

)