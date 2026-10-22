(define (problem deliver_crates)
  (:domain logistics_warehouse)

  (:objects
    t1 - truck
    h1 - hoist
    c1 - crate
    c2 - crate
    p1 - pallet
    p2 - pallet
    loc_a - location
    loc_b - location
  )

  (:init
    (at t1 loc_a)
    (at h1 loc_a)
    (on c1 p1)
    (on c2 p2)
    (at p1 loc_a)
    (at p2 loc_a)
    (empty t1)
  )

  (:goal (and (on c1 p2) (on c2 p1) (at c1 loc_b) (at c2 loc_b)))
)