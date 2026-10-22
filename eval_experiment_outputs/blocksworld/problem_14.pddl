(define (problem logistics_problem)
  (:domain blocksworld)

  (:objects
    t1 - truck
    p1 - airplane
    pkg1 - package
    loc1 - location
    apt1 - location
    apt2 - location
    city1 - city
    city2 - city
  )

  (:init
    (at pkg1 loc1)
    (at t1 loc1)
    (at p1 apt1)
    (in-city loc1 city1)
    (in-city apt1 city1)
    (in-city apt2 city2)
    (airport apt1)
    (airport apt2)
  )

  (:goal (and (at pkg1 apt2)))
)