(define (problem depots_problem)
  (:domain depots_domain)

  (:objects
    t1 - truck
    h1 - hoist
    c1 - crate
    p1 - pallet
    d1 - depot
  )

  (:init
    (at h1 d1)
    (on c1 p1)
    (at t1 d1)
    (clear h1)
  )

  (:goal (and (loaded t1 c1)))
)