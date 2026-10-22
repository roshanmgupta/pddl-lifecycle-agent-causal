(define (problem instance-1)
  (:domain zenotravel02)

  (:objects
    plane1 - aircraft
    person1 - person
    person2 - person
    city0 - city
    city1 - city
    city2 - city
    fl0 - flight_level
    fl1 - flight_level
    fl2 - flight_level
    fl3 - flight_level
    fl4 - flight_level
    fl5 - flight_level
    fl6 - flight_level
  )

  (:init
    (is_aircraft plane1)
    (is_person person1)
    (is_person person2)
    (is_city city0)
    (is_city city1)
    (is_city city2)
    (is_flight_level fl0)
    (is_flight_level fl1)
    (is_flight_level fl2)
    (is_flight_level fl3)
    (is_flight_level fl4)
    (is_flight_level fl5)
    (is_flight_level fl6)
    (at plane1 city0)
    (fuel_level plane1 fl1)
    (person_at person1 city0)
    (person_at person2 city2)
    (next fl0 fl1)
    (next fl1 fl2)
    (next fl2 fl3)
    (next fl3 fl4)
    (next fl4 fl5)
    (next fl5 fl6)
  )

  (:goal (and (at plane1 city1) (person_at person1 city0) (person_at person2 city2)))
)