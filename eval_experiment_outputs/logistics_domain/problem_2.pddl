(define (problem logistics_problem)
  (:domain logistics_domain)

  (:objects
    package3 - obj
    package2 - obj
    package1 - obj
    city5 - city
    city4 - city
    city3 - city
    city2 - city
    city1 - city
    truck5 - truck
    truck4 - truck
    truck3 - truck
    truck2 - truck
    truck1 - truck
    plane2 - airplane
    plane1 - airplane
    city5-1 - location
    city4-1 - location
    city3-1 - location
    city2-1 - location
    city1-1 - location
    city5-2 - airport
    city4-2 - airport
    city3-2 - airport
    city2-2 - airport
    city1-2 - airport
  )

  (:init
    (is_obj package3)
    (is_obj package2)
    (is_obj package1)
    (is_city city5)
    (is_city city4)
    (is_city city3)
    (is_city city2)
    (is_city city1)
    (is_truck truck5)
    (is_truck truck4)
    (is_truck truck3)
    (is_truck truck2)
    (is_truck truck1)
    (is_airplane plane2)
    (is_airplane plane1)
    (is_location city5-1)
    (is_location city4-1)
    (is_location city3-1)
    (is_location city2-1)
    (is_location city1-1)
    (is_airport city5-2)
    (is_airport city4-2)
    (is_airport city3-2)
    (is_airport city2-2)
    (is_airport city1-2)
    (in_city city5-2 city5)
    (in_city city5-1 city5)
    (in_city city4-2 city4)
    (in_city city4-1 city4)
    (in_city city3-2 city3)
    (in_city city3-1 city3)
    (in_city city2-2 city2)
    (in_city city2-1 city2)
    (in_city city1-2 city1)
    (in_city city1-1 city1)
    (at plane2 city1-2)
    (at plane1 city2-2)
    (at truck5 city5-1)
    (at truck4 city4-1)
    (at truck3 city3-1)
    (at truck2 city2-1)
    (at truck1 city1-1)
    (at package3 city1-1)
    (at package2 city1-2)
    (at package1 city4-1)
  )

  (:goal (and (at package3 city1-2) (at package2 city1-1) (at package1 city3-2)))
)