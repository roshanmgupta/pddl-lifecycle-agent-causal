(define (problem instance-1)
  (:domain satellite)

  (:objects
    satellite0 - satellite
    instrument0 - instrument
    instrument1 - instrument
    image0 - mode
    GroundStation0 - direction
    GroundStation1 - direction
    Star2 - direction
  )

  (:init
    (supports instrument0 image0)
    (calibration_target instrument0 GroundStation1)
    (supports instrument1 image0)
    (calibration_target instrument1 GroundStation1)
    (on_board instrument0 satellite0)
    (on_board instrument1 satellite0)
    (power_available satellite0)
    (pointing_at satellite0 Star2)
    (power_on instrument0)
    (calibrated instrument0)
  )

  (:goal (and (has_image Star2 image0)))
)