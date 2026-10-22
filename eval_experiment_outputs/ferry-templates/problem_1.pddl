(define (problem instance-1)
  (:domain ferry-templates)

  (:objects
    l0 - location
    l1 - location
    c0 - car
    c1 - car
    c2 - car
  )

  (:init
    (not-eq l0 l1)
    (not-eq l1 l0)
    (empty-ferry)
    (at c0 l0)
    (at c1 l0)
    (at c2 l0)
    (at-ferry l1)
  )

  (:goal (and (at c0 l1) (at c1 l0) (at c2 l0)))
)