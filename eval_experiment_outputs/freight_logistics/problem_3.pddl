(define (problem deliver_crates)
  (:domain freight_logistics)

  (:objects
    t1 - truck
    c1 - crate
    c2 - crate
    l1 - location
    l2 - location
    h1 - hoist
    p1 - pallet
  )

  (:init
    (truck_at t1 l1)
    (crate_at c1 l1)
    (crate_at c2 l1)
    (hoist_at h1 l1)
    (empty t1)
    (connected l1 l2)
    (holding h1 c1)
  )

  (:goal (and (crate_at c1 l2) (on_crate_crate c2 c1)))
)