(define (problem miconic_elevator_p0)
  (:domain miconic_elevator)

  (:objects
    p0 - passenger
    f0 - floor
    f1 - floor
  )

  (:init
    (above f0 f1)
    (lift-at f0)
    (origin p0 f1)
    (destin p0 f0)
  )

  (:goal (and (served p0)))
)