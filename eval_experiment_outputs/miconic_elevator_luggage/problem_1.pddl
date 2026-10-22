(define (problem miconic_passenger_luggage_problem)
  (:domain miconic_elevator_luggage)

  (:objects
    f0 - floor
    f1 - floor
    p1 - passenger
    lug1 - luggage
  )

  (:init
    (above f0 f1)
    (lift-at f0)
    (passenger-at p1 f1)
    (origin p1 f1)
    (destin p1 f0)
    (luggage-at lug1 f0)
  )

  (:goal (and (served p1) (luggage-at lug1 f1)))
)