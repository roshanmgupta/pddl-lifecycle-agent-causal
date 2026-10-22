(define (problem instance-1)
  (:domain logistics)

  (:objects
    a0 a1 - airplane
    c0 c1 - city
    t0 t1 - truck
    l0-0 l1-0 - airport
    p0 - obj
  )

  (:init
    (at a0 l0-0)
    (at a1 l0-0)
    (at t0 l0-0)
    (at t1 l1-0)
    (at-city l0-0 c0)
    (at-city l1-0 c1)
    (at-airport l0-0)
    (at-airport l1-0)
    (at p0 l1-0)
  )

  (:goal (and (at p0 l0-0)))
)