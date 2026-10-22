(define (problem logistics_blocksworld_problem)
  (:domain logistics_blocksworld)

  (:objects
    t1 - truck
    h1 - hoist
    c1 - crate
    p1 - pallet
    d1 - depot
    d2 - depot
  )

  (:init
    (at t1 d1)
    (at h1 d1)
    (at c1 d1)
    (on c1 p1)
    (clear c1)
    (available h1)
  )

  (:goal (and (at t1 d2) (in c1 t1)))
)