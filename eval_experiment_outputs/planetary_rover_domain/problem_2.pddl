(define (problem rover_soil_communication)
  (:domain planetary_rover_domain)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    l1 - lander
  )

  (:init
    (at r1 w1)
    (lander_at l1 w2)
  )

  (:goal (and (at r1 w2) (communicated_soil r1 l1)))
)