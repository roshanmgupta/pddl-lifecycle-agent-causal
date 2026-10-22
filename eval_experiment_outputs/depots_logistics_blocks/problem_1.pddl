(define (problem depot_scenario)
  (:domain depots_logistics_blocks)

  (:objects
    t1 - truck
    h1 - hoist
    d1 - depot
    c1 - crate
    p1 - pallet
  )

  (:init
    (at t1 d1)
    (at h1 d1)
    (at c1 d1)
    (on c1 p1)
    (at p1 d1)
    (available h1)
    (clear c1)
  )

  (:goal (and (in c1 t1)))
)