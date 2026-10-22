(define (problem logistics_scenario_1)
  (:domain logistics_domain)

  (:objects
    t1 - truck
    p1 - airplane
    pkg1 - package
    loc1 - location
    apt1 - airport
    apt2 - airport
  )

  (:init
    (at_pkg pkg1 loc1)
    (at_truck t1 loc1)
    (at_airplane p1 apt1)
    (same_city loc1 apt1)
    (same_city apt1 loc1)
  )

  (:goal (and (at_pkg pkg1 apt2)))
)