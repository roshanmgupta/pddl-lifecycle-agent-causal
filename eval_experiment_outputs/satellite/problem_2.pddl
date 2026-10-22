(define (problem sat_prob_01)
  (:domain satellite)

  (:objects
    sat1 - satellite
    dir1 - direction
    dir2 - direction
    inst1 - instrument
    spectrograph - mode
  )

  (:init
    (on-board inst1 sat1)
    (supports inst1 spectrograph)
    (pointing sat1 dir1)
    (power-avail sat1)
    (power-on inst1)
    (calibrated inst1)
  )

  (:goal (and (have-image dir2 spectrograph)))
)