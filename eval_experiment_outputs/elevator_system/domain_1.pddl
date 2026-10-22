(define (domain elevator_system)
  (:requirements :strips :typing)

  (:types
    count elevator floor passenger - object
    fast_elevator slow_elevator - elevator
  )

  (:predicates
    (at_floor ?p - passenger ?f - floor)
    (in_elevator ?p - passenger ?e - elevator)
    (elevator_at ?e - elevator ?f - floor)
    (can_serve ?e - elevator ?f - floor)
    (adjacent ?f1 - floor ?f2 - floor)
    (fast_connected ?f1 - floor ?f2 - floor)
    (passengers_count ?e - elevator ?c - count)
    (next_count ?c1 - count ?c2 - count)
  )

  (:action move_slow
    :parameters (?e - slow_elevator ?from - floor ?to - floor)
    :precondition (and (elevator_at ?e ?from) (can_serve ?e ?to) (adjacent ?from ?to))
    :effect (and (not (elevator_at ?e ?from)) (elevator_at ?e ?to))
  )

  (:action move_fast
    :parameters (?e - fast_elevator ?from - floor ?to - floor)
    :precondition (and (elevator_at ?e ?from) (can_serve ?e ?to) (fast_connected ?from ?to))
    :effect (and (not (elevator_at ?e ?from)) (elevator_at ?e ?to))
  )

  (:action board
    :parameters (?p - passenger ?e - elevator ?f - floor ?n1 - count ?n2 - count)
    :precondition (and (at_floor ?p ?f) (elevator_at ?e ?f) (can_serve ?e ?f) (passengers_count ?e ?n1) (next_count ?n1 ?n2))
    :effect (and (not (at_floor ?p ?f)) (in_elevator ?p ?e) (not (passengers_count ?e ?n1)) (passengers_count ?e ?n2))
  )

  (:action leave
    :parameters (?p - passenger ?e - elevator ?f - floor ?n1 - count ?n2 - count)
    :precondition (and (in_elevator ?p ?e) (elevator_at ?e ?f) (can_serve ?e ?f) (passengers_count ?e ?n2) (next_count ?n1 ?n2))
    :effect (and (not (in_elevator ?p ?e)) (at_floor ?p ?f) (not (passengers_count ?e ?n2)) (passengers_count ?e ?n1))
  )

)