(define (problem rover_mission_1)
  (:domain planetary_rover_exploration)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    w3 - waypoint
    lander1 - lander
    cam1 - camera
    drill1 - drill
    spec1 - spectrometer
    antenna1 - antenna
    store1 - sample_store
    calib1 - calibration_target
    obj1 - objective
    data1 - data
    data2 - data
  )

  (:init
    (at r1 w1)
    (connected w1 w2)
    (connected w2 w3)
    (connected w1 w3)
    (energy_available r1)
    (has_camera r1 cam1)
    (has_drill r1 drill1)
    (has_spectrometer r1 spec1)
    (has_antenna r1 antenna1)
    (has_sample_store r1 store1)
    (sample_store_empty store1)
    (calibration_target_visible calib1 w2)
    (objective_at obj1 w2)
    (line_of_sight w2 lander1)
  )

  (:goal (and (transmitted data1) (transmitted data2) (not (stored r1 data1)) (not (stored r1 data2))))
)