(define (problem sat_prob_power)
  (:domain satellite)

  (:objects
    sat1 - satellite
    dir1 - direction
    dir2 - direction
    inst1 - instrument
    inst2 - instrument
    mode1 - mode
  )

  (:init
    (on-board inst1 sat1)
    (on-board inst2 sat1)
    (power-avail sat1)
    (pointing sat1 dir1)
  )

  (:goal (and (power-on inst1) (power-on inst2)))
)