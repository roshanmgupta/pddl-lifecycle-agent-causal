(define (problem instance-1)
  (:domain transport14)

  (:objects
    loc-1 - location
    loc-2 - location
    loc-3 - location
    loc-4 - location
    loc-5 - location
    0 - capacity-number
    1 - capacity-number
    2 - capacity-number
    3 - capacity-number
    4 - capacity-number
    truck-1 - vehicle
    truck-2 - vehicle
    package-1 - package
    package-2 - package
    package-3 - package
    package-4 - package
  )

  (:init
    (capacity-predecessor 0 1)
    (capacity-predecessor 1 2)
    (capacity-predecessor 2 3)
    (capacity-predecessor 3 4)
    (road loc-3 loc-1)
    (road loc-1 loc-3)
    (road loc-3 loc-2)
    (road loc-2 loc-3)
    (road loc-4 loc-1)
    (road loc-1 loc-4)
    (road loc-4 loc-3)
    (road loc-3 loc-4)
    (road loc-5 loc-2)
    (road loc-2 loc-5)
    (road loc-5 loc-3)
    (road loc-3 loc-5)
    (at package-1 loc-1)
    (at package-2 loc-1)
    (at package-3 loc-3)
    (at package-4 loc-2)
    (at truck-1 loc-2)
    (capacity truck-1 3)
    (at truck-2 loc-1)
    (capacity truck-2 2)
  )

  (:goal (and (at package-1 loc-2) (at package-2 loc-2) (at package-3 loc-1) (at package-4 loc-5)))
)