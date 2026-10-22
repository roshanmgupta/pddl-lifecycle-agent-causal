(define (problem instance-1)
  (:domain logistics_planbench)

  (:objects
    a0 - airplane
    a1 - airplane
    c0 - city
    c1 - city
    t0 - truck
    t1 - truck
    l0-0 - location
    l1-0 - location
    p0 - package
  )

  (:init
    (location-in-city l0-0 c0)
    (location-in-city l1-0 c1)
    (airport l0-0)
    (airport l1-0)
    (truck-at t0 l0-0)
    (truck-at t1 l1-0)
    (at p0 l1-0)
    (airplane-at a0 l0-0)
    (airplane-at a1 l0-0)
  )

  (:goal (and (at p0 l0-0)))
)