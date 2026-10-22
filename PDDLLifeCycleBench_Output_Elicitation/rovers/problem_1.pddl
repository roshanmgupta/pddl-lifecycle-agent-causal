(define (problem instance-1)
  (:domain rovers)

  (:objects
    general - lander
    colour high_res low_res - mode
    rover0 - rover
    rover0store - store
    waypoint0 waypoint1 waypoint2 - waypoint
    camera0 - camera
    objective0 - objective
  )

  (:init
    (visible waypoint0 waypoint1)
    (visible waypoint1 waypoint0)
    (visible waypoint0 waypoint2)
    (visible waypoint2 waypoint0)
    (visible waypoint1 waypoint2)
    (visible waypoint2 waypoint1)
    (at-sample waypoint0)
    (at-sample waypoint1)
    (at-sample waypoint2)
    (at-sample waypoint2)
    (at general waypoint0)
    (channel-free general)
    (at rover0 waypoint0)
    (available rover0)
    (store-of rover0store rover0)
    (empty rover0store)
    (equipped-for-soil-analysis rover0)
    (equipped-for-rock-analysis rover0)
    (equipped-for-imaging rover0)
    (can-traverse rover0 waypoint0 waypoint1)
    (can-traverse rover0 waypoint1 waypoint0)
    (can-traverse rover0 waypoint0 waypoint2)
    (can-traverse rover0 waypoint2 waypoint0)
    (on-board camera0 rover0)
    (calibration-target camera0 objective0)
    (supports camera0 colour)
    (supports camera0 high_res)
    (supports camera0 low_res)
    (visible objective0 waypoint2)
  )

  (:goal (and (communicated-soil-data waypoint2) (communicated-rock-data waypoint1) (communicated-image-data objective0 colour)))
)