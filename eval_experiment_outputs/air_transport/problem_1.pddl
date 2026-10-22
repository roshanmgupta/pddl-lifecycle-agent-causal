(define (problem transport_passengers)
  (:domain air_transport)

  (:objects
    a1 - aircraft
    c1 - city
    c2 - city
    c3 - city
    p1 - passenger
    p2 - passenger
    f1 - fuel_level
    f2 - fuel_level
    normal - speed_mode
    zoom - speed_mode
  )

  (:init
    (at_aircraft a1 c1)
    (at_passenger p1 c1)
    (at_passenger p2 c1)
    (current_fuel a1 f1)
    (current_speed a1 normal)
    (can_refuel a1 c1)
    (can_refuel a1 c2)
    (can_refuel a1 c3)
  )

  (:goal (and (at_passenger p1 c3) (at_passenger p2 c2)))
)