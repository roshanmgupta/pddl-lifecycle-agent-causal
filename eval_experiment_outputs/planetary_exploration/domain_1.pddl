(define (domain planetary_exploration)
  (:requirements :strips :typing)

  (:types
    equipment image_type lander rover waypoint - object
    camera rock_sampling_tool soil_analysis_tool - equipment
  )

  (:predicates
    (at ?r - rover ?w - waypoint)
    (carrying ?r - rover ?e - equipment)
    (has_line_of_sight ?w1 - waypoint ?w2 - waypoint)
    (has_line_of_sight_to_lander ?w - waypoint ?l - lander)
    (sample_collected ?r - rover ?w - waypoint)
    (camera_calibrated ?c - camera)
    (image_taken ?r - rover ?w - waypoint ?type - image_type)
    (data_transmitted ?r - rover ?l - lander)
  )

  (:action navigate
    :parameters (?r - rover ?from - waypoint ?to - waypoint)
    :precondition (and (at ?r ?from) (has_line_of_sight ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action collect_soil_sample
    :parameters (?r - rover ?w - waypoint ?tool - soil_analysis_tool)
    :precondition (and (at ?r ?w) (carrying ?r ?tool))
    :effect (sample_collected ?r ?w)
  )

  (:action collect_rock_sample
    :parameters (?r - rover ?w - waypoint ?tool - rock_sampling_tool)
    :precondition (and (at ?r ?w) (carrying ?r ?tool))
    :effect (sample_collected ?r ?w)
  )

  (:action calibrate_camera
    :parameters (?r - rover ?c - camera)
    :precondition (carrying ?r ?c)
    :effect (camera_calibrated ?c)
  )

  (:action take_panoramic_image
    :parameters (?r - rover ?w - waypoint ?c - camera ?type - image_type)
    :precondition (and (at ?r ?w) (carrying ?r ?c) (camera_calibrated ?c))
    :effect (image_taken ?r ?w ?type)
  )

  (:action take_high_resolution_image
    :parameters (?r - rover ?w - waypoint ?c - camera ?type - image_type)
    :precondition (and (at ?r ?w) (carrying ?r ?c) (camera_calibrated ?c))
    :effect (image_taken ?r ?w ?type)
  )

  (:action transmit_data
    :parameters (?r - rover ?w - waypoint ?l - lander)
    :precondition (and (at ?r ?w) (has_line_of_sight_to_lander ?w ?l) (sample_collected ?r ?w))
    :effect (data_transmitted ?r ?l)
  )

)