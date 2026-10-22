(define (problem freight_distribution_problem)
  (:domain freight_distribution_domain)

  (:objects
    l1 - depot
    l2 - distributor
    crane1 - crane
    crane2 - crane
    truck1 - truck
    s1 - capacity_slot
    s2 - capacity_slot
    p1 - pallet
    p2 - pallet
    c1 - crate
    c2 - crate
  )

  (:init
    (connected l1 l2)
    (connected l2 l1)
    (crane_at crane1 l1)
    (crane_at crane2 l2)
    (truck_at truck1 l1)
    (slot_of s1 truck1)
    (slot_of s2 truck1)
    (slot_empty s1)
    (slot_empty s2)
    (pallet_at p1 l1)
    (pallet_at p2 l2)
    (pallet_empty p2)
    (hoist_empty crane1)
    (hoist_empty crane2)
    (crate_at c1 l1)
    (crate_at c2 l1)
    (on_pallet c1 p1)
    (on c2 c1)
    (clear c2)
  )

  (:goal (and (crate_at c2 l2) (on_pallet c2 p2) (clear c2)))
)