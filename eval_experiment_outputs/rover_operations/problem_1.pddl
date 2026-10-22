(define (problem rover_mission_1)
  (:domain rover_operations)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    w3 - waypoint
    s1 - store
    cam1 - camera
    m1 - mode
    l1 - lander
    o1 - objective
  )

  (:init
    (can_traverse r1 w1 w2)
    (can_traverse r1 w2 w3)
    (available r1)
    (at r1 w1)
    (visible w1 w2)
    (visible w2 w3)
    (at_soil_sample w2)
    (equipped_for_soil_analysis r1)
    (store_of s1 r1)
    (empty s1)
    (equipped_for_imaging r1)
    (calibration_target cam1 o1)
    (on_board cam1 r1)
    (supports cam1 m1)
    (at_lander l1 w3)
    (channel_free l1)
  )

  (:goal (and (communicated_soil_data w2) (communicated_image_data o1 m1)))
)