(define (problem logistics_prob_01)
  (:domain logistics)

  (:objects
    pkg1 - package
    t1 - truck
    loc1 - location
  )

  (:init
    (at pkg1 loc1)
    (at t1 loc1)
  )

  (:goal (and ))
)