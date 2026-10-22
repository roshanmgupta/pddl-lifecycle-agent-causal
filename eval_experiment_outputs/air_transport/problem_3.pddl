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
  )

  (:init
    (at_aircraft a1 c1)
    (in_city p1 c1)
    (in_city p2 c1)
    (target_city p1 c3)
    (target_city p2 c2)
    (has_fuel a1 f1)
    (can_fly_normal a1)
    (can_fly_zoom a1)
    (at_passenger p1 c1)
    (at_passenger p2 c1)
  )

  (:goal (and (in_city p1 c3) (in_city p2 c2)))
)