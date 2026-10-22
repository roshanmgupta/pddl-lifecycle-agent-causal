(define (problem depots_problem)
  (:domain depots_domain)

  (:objects
    t1 - truck
    h1 - hoist
    c1 - crate
    p1 - pallet
    d1 - location
  )

  (:init
    (at_truck t1 d1)
    (at_hoist h1 d1)
    (on c1 p1)
    (at_crate c1 d1)
    (clear p1)
  )

  (:goal (and (loaded c1 t1)))
)