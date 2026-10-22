(define (problem satellite_observation_problem)
  (:domain earth_observation_satellite)

  (:objects
    sat1 - satellite
    ir1 - instrument
    spec1 - instrument
    ir_mode - imaging_mode
    spec_mode - imaging_mode
    cal_target - calibration_target
    sky1 - sky_phenomenon
    land1 - terrestrial_target
  )

  (:init
    (on_satellite ir1 sat1)
    (on_satellite spec1 sat1)
    (instrument_mode ir1 ir_mode)
    (instrument_mode spec1 spec_mode)
    (bus_free sat1)
    (pointing sat1 cal_target)
  )

  (:goal (and (captured ir1 sky1) (captured spec1 land1)))
)