(define (problem depotprob7512)
  (:domain Depot)

  (:objects
    depot0 - Depot
    distributor0 - Distributor
    distributor1 - Distributor
    truck0 - Truck
    truck1 - Truck
    pallet0 - Pallet
    pallet1 - Pallet
    pallet2 - Pallet
    crate0 - Crate
    crate1 - Crate
    crate2 - Crate
    crate3 - Crate
    hoist0 - Hoist
    hoist1 - Hoist
    hoist2 - Hoist
  )

  (:init
    (at pallet0 depot0)
    (clear crate0)
    (at pallet1 distributor0)
    (clear crate3)
    (at pallet2 distributor1)
    (clear crate2)
    (at truck0 depot0)
    (at truck1 depot0)
    (at hoist0 depot0)
    (available hoist0)
    (at hoist1 distributor0)
    (available hoist1)
    (at hoist2 distributor1)
    (available hoist2)
    (at crate0 depot0)
    (on crate0 pallet0)
    (at crate1 distributor1)
    (on crate1 pallet2)
    (at crate2 distributor1)
    (on crate2 crate1)
    (at crate3 distributor0)
    (on crate3 pallet1)
  )

  (:goal (and (on crate0 pallet2) (on crate1 crate3) (on crate2 pallet0) (on crate3 pallet1)))
)