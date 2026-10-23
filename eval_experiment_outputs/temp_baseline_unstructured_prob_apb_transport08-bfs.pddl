(define (problem instance-1)
  (:domain transport08-bfs)
  (:objects
    city-loc-1 city-loc-2 city-loc-3 - location
    truck-1 truck-2 - vehicle
    package-1 package-2 - package
    capacity-0 capacity-1 capacity-2 capacity-3 capacity-4 - capacity-number
  )
  (:init
    (capacity-predecessor capacity-0 capacity-1)
    (capacity-predecessor capacity-1 capacity-2)
    (capacity-predecessor capacity-2 capacity-3)
    (capacity-predecessor capacity-3 capacity-4)
    (road city-loc-3 city-loc-1)
    (road city-loc-1 city-loc-3)
    (road city-loc-3 city-loc-2)
    (road city-loc-2 city-loc-3)
    (at-package package-1 city-loc-3)
    (at-package package-2 city-loc-3)
    (at truck-1 city-loc-3)
    (has-capacity truck-1 capacity-4)
    (at truck-2 city-loc-1)
    (has-capacity truck-2 capacity-3)
  )
  (:goal
    (and
      (at-package package-1 city-loc-2)
      (at-package package-2 city-loc-2)
    )
  )
)