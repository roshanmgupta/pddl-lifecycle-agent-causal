(define (problem mars_exploration_mission)
  (:domain planetary_exploration)

  (:objects
    r1 - rover
    w1 - waypoint
    w2 - waypoint
    w3 - waypoint
    l1 - lander
    soil_tool1 - soil_analysis_tool
    rock_tool1 - rock_sampling_tool
    camera1 - camera
    panoramic - image_type
    high_resolution - image_type
  )

  (:init
    (at r1 w1)
    (carrying r1 soil_tool1)
    (carrying r1 rock_tool1)
    (carrying r1 camera1)
    (has_line_of_sight w1 w2)
    (has_line_of_sight w2 w3)
    (has_line_of_sight_to_lander w3 l1)
  )

  (:goal (and (sample_collected r1 w2) (sample_collected r1 w3) (image_taken r1 w2 panoramic) (image_taken r1 w3 high_resolution) (data_transmitted r1 l1)))
)