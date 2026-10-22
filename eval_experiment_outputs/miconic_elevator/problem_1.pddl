(define (problem miconic_elevator_p0)
  (:domain miconic_elevator)

  (:objects
    p0 - passenger
    f0 - floor
    f1 - floor
  )

  (:init
    (directly_below f1 f0)
    (lift_at f0)
    (origin p0 f1)
    (destination p0 f0)
  )

  (:goal (and (served p0)))
)