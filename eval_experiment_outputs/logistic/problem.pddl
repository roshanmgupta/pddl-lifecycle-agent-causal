(define (problem logistics_problem)
  (:domain logistics)

  (:objects
    t1 - truck
    p1 - airplane
    pkg1 - package
    loc1 - location
    apt1 - airport
    apt2 - airport
  )

  (:init
    (at t1 loc1)
    (at pkg1 loc1)
    (at-airport p1 apt1)
  )

  (:goal (and (at-airport pkg1 apt2)))
)