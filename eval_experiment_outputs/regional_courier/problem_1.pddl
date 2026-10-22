(define (problem courier_delivery)
  (:domain regional_courier)

  (:objects
    d1 - driver
    t1 - truck
    p1 - package
    loc_a - location
    loc_b - location
  )

  (:init
    (at d1 loc_a)
    (at t1 loc_a)
    (at p1 loc_a)
    (footpath loc_a loc_b)
    (road loc_a loc_b)
    (certified d1)
    (active d1)
  )

  (:goal (and (at p1 loc_b)))
)