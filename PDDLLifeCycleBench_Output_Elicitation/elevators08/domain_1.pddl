(define (domain elevators08)
  (:requirements :strips :typing)

  (:types
    count elevator passenger - object
    fast-elevator slow-elevator - elevator
  )

  (:predicates
    (at ?e - object ?c - count)
    (has ?e - elevator ?n - count)
    (can-hold ?e - elevator ?n - count)
    (reachable ?e - elevator ?c - count)
    (next-to ?c1 - count ?c2 - count)
    (above ?c1 - count ?c2 - count)
    (boarded ?p - passenger ?e - elevator)
    (passengers ?e - elevator ?n - count)
  )

  (:action move_slow_elevator_up
    :parameters (?e - slow-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable ?e ?to))
    :effect (and (at ?e ?to) (not (at ?e ?from)))
  )

  (:action move_slow_elevator_down
    :parameters (?e - slow-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?to ?from) (reachable ?e ?to))
    :effect (and (at ?e ?to) (not (at ?e ?from)))
  )

  (:action move_fast_elevator_up
    :parameters (?e - fast-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable ?e ?to))
    :effect (and (at ?e ?to) (not (at ?e ?from)))
  )

  (:action move_fast_elevator_down
    :parameters (?e - fast-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?to ?from) (reachable ?e ?to))
    :effect (and (at ?e ?to) (not (at ?e ?from)))
  )

  (:action board_passenger
    :parameters (?p - passenger ?e - elevator ?c - count ?d - count ?e_count - count)
    :precondition (and (at ?e ?c) (at ?p ?c) (passengers ?e ?d) (next-to ?d ?e_count) (can-hold ?e ?e_count))
    :effect (and (boarded ?p ?e) (passengers ?e ?e_count) (not (at ?p ?c)) (not (passengers ?e ?d)))
  )

  (:action leave_elevator
    :parameters (?p - passenger ?e - elevator ?c - count ?d - count ?e_count - count)
    :precondition (and (at ?e ?c) (boarded ?p ?e) (passengers ?e ?d) (next-to ?e_count ?d))
    :effect (and (at ?p ?c) (passengers ?e ?e_count) (not (boarded ?p ?e)) (not (passengers ?e ?d)))
  )

)