(define (problem depot_prob_01)
  (:domain depot)

  (:objects
    d1 - depot
    h1 - hoist
    c1 - crate
    p1 - pallet
  )

  (:init
    (at h1 d1)
    (at p1 d1)
    (at c1 d1)
    (on c1 p1)
    (clear c1)
    (available h1)
  )

  (:goal (and (lifting h1 c1)))
)