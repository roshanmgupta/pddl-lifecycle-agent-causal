(define (problem deliver_crates)
  (:domain freight_logistics)

  (:objects
    truck1 - truck
    crate1 - crate
    crate2 - crate
    depot1 - location
    distributor1 - location
    pallet1 - pallet
    hoist1 - hoist
  )

  (:init
    (at_movable truck1 depot1)
    (at_movable crate1 depot1)
    (at_movable crate2 depot1)
    (on_pallet crate1 pallet1)
    (empty truck1)
    (holding hoist1 crate2)
    (at_movable pallet1 depot1)
  )

  (:goal (and (at_movable crate1 distributor1) (on_crate crate2 crate1)))
)