(define (domain satellite_imaging)
  (:requirements :strips :typing)

  (:types
    instrument mode satellite target - object
  )

  (:predicates
    (powered_on ?i - instrument)
    (calibrated ?i - instrument ?t - target)
    (aimed_at ?s - satellite ?t - target)
    (image_captured ?s - satellite ?t - target ?m - mode)
  )

  (:action turn_satellite
    :parameters (?s - satellite ?from - target ?to - target)
    :precondition (aimed_at ?s ?from)
    :effect (and (not (aimed_at ?s ?from)) (aimed_at ?s ?to))
  )

  (:action calibrate_instrument
    :parameters (?i - instrument ?s - satellite ?t - target)
    :precondition (and (powered_on ?i) (aimed_at ?s ?t))
    :effect (calibrated ?i ?t)
  )

  (:action capture_image
    :parameters (?s - satellite ?t - target ?m - mode ?i - instrument)
    :precondition (and (aimed_at ?s ?t) (calibrated ?i ?t) (powered_on ?i))
    :effect (image_captured ?s ?t ?m)
  )

)