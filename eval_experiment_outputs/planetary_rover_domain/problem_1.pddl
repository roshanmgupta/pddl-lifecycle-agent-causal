(define (problem rover_sample_soil_problem)
  (:domain planetary_rover_domain)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    l1 - lander
  )

  (:init
    (at r1 w1)
    (at_lander l1 w2)
    (soil_at w1)
  )

  (:goal (and (communicated_soil r1 l1)))
)