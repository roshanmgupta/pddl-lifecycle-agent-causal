(define (problem deliver_and_stack_crates)
  (:domain freight_logistics)

  (:objects
    t1 - truck
    c1 - crate
    c2 - urgent_cargo
    l1 - location
    l2 - location
    h1 - hoist
    p1 - pallet
  )

  (:init
    (at-truck t1 l1)
    (at-crate c1 l1)
    (at-crate c2 l1)
    (hoist-at h1 l1)
    (empty-hoist h1)
    (on-pallet c1 p1)
    (at-pallet p1 l1)
    (urgent c2)
  )

  (:goal (and (at-crate c1 l2) (on c2 c1)))
)