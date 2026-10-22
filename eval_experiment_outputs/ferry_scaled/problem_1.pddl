(define (problem instance-19)
  (:domain ferry_scaled)

  (:objects
    l0 - location
    l1 - location
    l2 - location
    c0 - car
    c1 - car
    c2 - car
    c3 - car
    c4 - car
    c5 - car
    c6 - car
    c7 - car
    c8 - car
    c9 - car
    c10 - car
    c11 - car
    c12 - car
    c13 - car
  )

  (:init
    (not-equal l0 l1)
    (not-equal l1 l0)
    (not-equal l0 l2)
    (not-equal l2 l0)
    (not-equal l1 l2)
    (not-equal l2 l1)
    (empty-ferry)
    (at c0 l2)
    (at c1 l2)
    (at c2 l0)
    (at c3 l0)
    (at c4 l1)
    (at c5 l1)
    (at c6 l1)
    (at c7 l0)
    (at c8 l0)
    (at c9 l2)
    (at c10 l1)
    (at c11 l1)
    (at c12 l0)
    (at c13 l1)
    (at-ferry l2)
  )

  (:goal (and (at c0 l2) (at c1 l2) (at c2 l1) (at c3 l2) (at c4 l2) (at c5 l2) (at c6 l0) (at c7 l0) (at c8 l2) (at c9 l1) (at c10 l0) (at c11 l2) (at c12 l2) (at c13 l2)))
)