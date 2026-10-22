(define (problem transport_passengers)
  (:domain elevator_domain)

  (:objects
    e0 - elevator
    f1 - floor
    f2 - floor
    f3 - floor
    p1 - passenger
    p2 - passenger
  )

  (:init
    (lift-at e0 f1)
    (at p1 f1)
    (at p2 f2)
  )

  (:goal (and (at p1 f3) (at p2 f1)))
)