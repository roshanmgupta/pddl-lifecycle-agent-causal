(define (problem delivery_coordination)
  (:domain transportation_logistics)

  (:objects
    d1 - driver
    t1 - truck
    p1 - package
    loc_a - location
    loc_b - location
    loc_c - location
  )

  (:init
    (at d1 loc_a)
    (at t1 loc_a)
    (at p1 loc_a)
    (path_connected loc_a loc_b)
    (road_connected loc_a loc_c)
    (road_connected loc_c loc_b)
  )

  (:goal (and (at p1 loc_b)))
)