(define (problem crate_in_truck)
  (:domain depot_logistics)

  (:objects
    t1 - vehicle
    h1 - hoist
    d1 - depot
    c1 - crate
    p1 - pallet
  )

  (:init
    (at t1 d1)
    (at_hoist h1 d1)
    (on_crate c1 p1)
    (on_pallet p1 d1)
  )

  (:goal (and (in_truck c1 t1)))
)