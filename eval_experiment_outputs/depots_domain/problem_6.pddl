(define (problem depots_problem)
  (:domain depots_domain)

  (:objects
    t1 - truck
    h1 - hoist
    d1 - depot
    c1 - crate
    p1 - pallet
  )

  (:init
    (at-hoist h1 d1)
    (at-truck t1 d1)
    (on c1 p1)
    (clear c1)
  )

  (:goal (and (in c1 t1)))
)