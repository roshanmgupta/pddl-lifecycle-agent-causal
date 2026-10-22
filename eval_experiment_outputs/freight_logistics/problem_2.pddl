(define (problem deliver_and_stack_crates)
  (:domain freight_logistics)

  (:objects
    truck1 - truck
    hoist1 - hoist
    hoist2 - hoist
    crate1 - crate
    crate2 - crate
    pallet1 - pallet
    depot1 - location
    depot2 - location
    distributor1 - location
  )

  (:init
    (at truck1 depot1)
    (at hoist1 depot1)
    (at hoist2 distributor1)
    (at pallet1 distributor1)
    (on crate1 pallet1)
    (empty hoist1)
    (empty hoist2)
    (at crate2 depot1)
  )

  (:goal (and (on crate2 crate1) (at crate2 distributor1)))
)