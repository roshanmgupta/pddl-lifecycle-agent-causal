(define (problem instance-1)
  (:domain ferry)

  (:objects
    l0 - location
    l1 - location
    c0 - car
    c1 - car
    c2 - car
  )

  (:init
    (not-equal l0 l1)
    (not-equal l1 l0)
    (ferry-empty)
    (at c0 l0)
    (at c1 l0)
    (at c2 l0)
    (at-ferry l1)
  )

  (:goal (and (at c0 l1) (at c1 l0) (at c2 l0)))
)