(define (domain elevators)
  (:requirements :strips :typing)

  (:types
    count elevator object passenger - object
    fast-elevator slow-elevator - elevator
  )

  (:predicates
    (at ?e - elevator ?c - count)
    (above ?c1 - count ?c2 - count)
    (next-to ?c1 - count ?c2 - count)
    (passengers ?e - elevator ?c - count)
    (can-hold ?e - elevator ?c - count)
    (reachable-by ?e - elevator ?c - count)
    (at-floor ?p - passenger ?c - count)
    (boarded ?p - passenger ?e - elevator)
  )

  (:action move-slow-elevator-down
    :parameters (?e - slow-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable-by ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action move-slow-elevator-up
    :parameters (?e - slow-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?to ?from) (reachable-by ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action move-fast-elevator-down
    :parameters (?e - fast-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable-by ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action move-fast-elevator-up
    :parameters (?e - fast-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?to ?from) (reachable-by ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action board-passenger
    :parameters (?p - passenger ?e - elevator ?c - count ?from - count ?to - count)
    :precondition (and (at ?e ?c) (at-floor ?p ?c) (passengers ?e ?from) (next-to ?from ?to) (can-hold ?e ?to))
    :effect (and (not (at-floor ?p ?c)) (not (passengers ?e ?from)) (boarded ?p ?e) (passengers ?e ?to))
  )

  (:action leave-elevator
    :parameters (?p - passenger ?e - elevator ?c - count ?from - count ?to - count)
    :precondition (and (at ?e ?c) (boarded ?p ?e) (passengers ?e ?from) (next-to ?to ?from))
    :effect (and (not (boarded ?p ?e)) (not (passengers ?e ?from)) (at-floor ?p ?c) (passengers ?e ?to))
  )

)