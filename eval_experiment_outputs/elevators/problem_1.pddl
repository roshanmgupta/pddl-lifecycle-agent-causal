(define (problem instance-1)
  (:domain elevators)

  (:objects
    n0 - count
    n1 - count
    n2 - count
    n3 - count
    n4 - count
    n5 - count
    n6 - count
    n7 - count
    n8 - count
    p0 - passenger
    p1 - passenger
    p2 - passenger
    fast0 - fast-elevator
    slow0-0 - slow-elevator
    slow1-0 - slow-elevator
  )

  (:init
    (next-to n0 n1)
    (next-to n1 n2)
    (next-to n2 n3)
    (next-to n3 n4)
    (next-to n4 n5)
    (next-to n5 n6)
    (next-to n6 n7)
    (next-to n7 n8)
    (above n0 n1)
    (above n0 n2)
    (above n0 n3)
    (above n0 n4)
    (above n0 n5)
    (above n0 n6)
    (above n0 n7)
    (above n0 n8)
    (above n1 n2)
    (above n1 n3)
    (above n1 n4)
    (above n1 n5)
    (above n1 n6)
    (above n1 n7)
    (above n1 n8)
    (above n2 n3)
    (above n2 n4)
    (above n2 n5)
    (above n2 n6)
    (above n2 n7)
    (above n2 n8)
    (above n3 n4)
    (above n3 n5)
    (above n3 n6)
    (above n3 n7)
    (above n3 n8)
    (above n4 n5)
    (above n4 n6)
    (above n4 n7)
    (above n4 n8)
    (above n5 n6)
    (above n5 n7)
    (above n5 n8)
    (above n6 n7)
    (above n6 n8)
    (above n7 n8)
    (at fast0 n0)
    (passengers fast0 n0)
    (can-hold fast0 n1)
    (can-hold fast0 n2)
    (can-hold fast0 n3)
    (reachable-by fast0 n0)
    (reachable-by fast0 n2)
    (reachable-by fast0 n4)
    (reachable-by fast0 n6)
    (reachable-by fast0 n8)
    (at slow0-0 n2)
    (passengers slow0-0 n0)
    (can-hold slow0-0 n1)
    (can-hold slow0-0 n2)
    (reachable-by slow0-0 n0)
    (reachable-by slow0-0 n1)
    (reachable-by slow0-0 n2)
    (reachable-by slow0-0 n3)
    (reachable-by slow0-0 n4)
    (at slow1-0 n4)
    (passengers slow1-0 n0)
    (can-hold slow1-0 n1)
    (can-hold slow1-0 n2)
    (reachable-by slow1-0 n4)
    (reachable-by slow1-0 n5)
    (reachable-by slow1-0 n6)
    (reachable-by slow1-0 n7)
    (reachable-by slow1-0 n8)
    (at-floor p0 n8)
    (at-floor p1 n3)
    (at-floor p2 n2)
  )

  (:goal (and (at-floor p0 n4) (at-floor p1 n6) (at-floor p2 n1)))
)