(define (problem zenotravel_problem)
  (:domain zenotravel)

  (:objects
    plane1 - aircraft
    person1 - person
    city0 - city
    city1 - city
    fl0 - flevel
    fl1 - flevel
    fl2 - flevel
  )

  (:init
    (at plane1 city0)
    (at person1 city0)
    (fuel-level plane1 fl2)
    (next fl0 fl1)
    (next fl1 fl2)
  )

  (:goal (and (at person1 city1) (at plane1 city1)))
)