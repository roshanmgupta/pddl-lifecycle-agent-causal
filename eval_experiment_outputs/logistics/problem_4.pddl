(define (problem instance-1)
  (:domain logistics)

  (:objects
    a0 - airplane
    a1 - airplane
    c0 - city
    c1 - city
    t0 - truck
    t1 - truck
    l0-0 - airport
    l1-0 - airport
    p0 - obj
  )

  (:init
    (is_at_vehicle t0 l0-0)
    (is_at_vehicle t1 l1-0)
    (is_at p0 l1-0)
    (is_at_vehicle a0 l0-0)
    (is_at_vehicle a1 l0-0)
    (is_in_city l0-0 c0)
    (is_in_city l1-0 c1)
    (is_airport l0-0)
    (is_airport l1-0)
  )

  (:goal (and (is_at p0 l0-0)))
)