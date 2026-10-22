(define (problem express_delivery)
  (:domain freight_logistics)

  (:objects
    t1 - truck
    d1 - depot
    d2 - depot
    c1 - cargo
  )

  (:init
    (at t1 d1)
    (carrying t1 c1)
    (urgent c1)
  )

  (:goal (and (at t1 d2)))
)