(define (problem elevator_problem)
  (:domain elevator_system)

  (:objects
    p1 - passenger
    p2 - passenger
    f0 - floor
    f1 - floor
    f2 - floor
    f3 - floor
    f4 - floor
    f5 - floor
    f6 - floor
    e_slow1 - slow_elevator
    e_slow2 - slow_elevator
    e_fast1 - fast_elevator
    n0 - count
    n1 - count
    n2 - count
  )

  (:init
    (elevator_at e_slow1 f0)
    (elevator_at e_slow2 f3)
    (elevator_at e_fast1 f0)
    (at_floor p1 f2)
    (at_floor p2 f1)
    (passengers_count e_slow1 n0)
    (passengers_count e_slow2 n0)
    (passengers_count e_fast1 n0)
    (next_count n0 n1)
    (next_count n1 n2)
    (can_serve e_slow1 f0)
    (can_serve e_slow1 f1)
    (can_serve e_slow1 f2)
    (can_serve e_slow1 f3)
    (can_serve e_slow2 f3)
    (can_serve e_slow2 f4)
    (can_serve e_slow2 f5)
    (can_serve e_slow2 f6)
    (can_serve e_fast1 f0)
    (can_serve e_fast1 f6)
    (adjacent f0 f1)
    (adjacent f1 f0)
    (adjacent f1 f2)
    (adjacent f2 f1)
    (adjacent f2 f3)
    (adjacent f3 f2)
    (adjacent f3 f4)
    (adjacent f4 f3)
    (adjacent f4 f5)
    (adjacent f5 f4)
    (adjacent f5 f6)
    (adjacent f6 f5)
    (fast_connected f0 f6)
    (fast_connected f6 f0)
  )

  (:goal (and (at_floor p1 f5) (at_floor p2 f6)))
)