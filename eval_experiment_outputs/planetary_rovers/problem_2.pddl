(define (problem rover_mission)
  (:domain planetary_rovers)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    s1 - store
    c1 - camera
    m1 - mode
    l1 - lander
    o1 - objective
  )

  (:init
    (at r1 w1)
    (can_traverse r1 w1 w2)
    (available r1)
    (visible w1 w2)
    (soil_sample_at w2)
    (equipped_for_soil_analysis r1)
    (store_of s1 r1)
    (empty s1)
    (channel_free l1)
    (lander_at l1 w1)
    (visible w1 w1)
    (visible w2 w2)
    (has_soil_analysis r1 w2)
  )

  (:goal (and (communicated_soil_data w2)))
)