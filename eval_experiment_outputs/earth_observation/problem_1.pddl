(define (problem earth_observation_problem)
  (:domain earth_observation)

  (:objects
    sat1 - satellite
    cam1 - instrument
    sens1 - instrument
    ir - mode
    spec - mode
    targ1 - target
    targ2 - target
    high - power_level
    medium - power_level
  )

  (:init
    (onboard cam1 sat1)
    (onboard sens1 sat1)
    (supports cam1 ir)
    (supports sens1 spec)
    (pointing sat1 targ1)
    (power_available sat1 high)
    (power_available sat1 medium)
  )

  (:goal (and (has_image targ1 ir) (has_image targ2 spec)))
)