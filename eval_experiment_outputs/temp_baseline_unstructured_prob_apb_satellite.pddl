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
    (calibration-target instrument0 GroundStation1)
    (supports instrument1 image0)
    (calibration-target instrument1 GroundStation1)
    (on-board instrument0 satellite0)
    (on-board instrument1 satellite0)
    (power-available satellite0)
    (pointing-at satellite0 Star2)
  )
  (:goal
    (has-image Star2 image0)
  )
)