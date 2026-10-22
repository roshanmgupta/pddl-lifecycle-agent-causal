(define (problem deliver_crates)
  (:domain freight_logistics)

  (:objects
    truck1 - truck
    crate1 - crate
    crate2 - crate
    pallet1 - pallet
    depot1 - location
    distributor1 - location
    hoist1 - hoist
  )

  (:init
    (at truck1 depot1)
    (at crate1 depot1)
    (at crate2 depot1)
    (on crate1 pallet1)
    (on crate2 pallet1)
    (empty truck1)
    (available hoist1)
    (at pallet1 depot1)
  )

  (:goal (and (at crate1 distributor1) (at crate2 distributor1)))
)