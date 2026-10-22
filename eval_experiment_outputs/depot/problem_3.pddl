(define (problem multi_hoist_depot)
  (:domain Depot)

  (:objects
    h1 - hoist
    h2 - hoist
    t1 - truck
    d1 - depot
    d2 - distributor
    c1 - crate
    c2 - crate
    p1 - pallet
    p2 - pallet
  )

  (:init
    (at h1 d1)
    (at h2 d1)
    (at t1 d1)
    (on c1 p1)
    (on c2 p2)
    (clear c1)
    (clear c2)
    (available h1)
    (available h2)
  )

  (:goal (and (in c1 t1) (in c2 t1)))
)