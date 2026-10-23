(define (domain elevators08)
  (:requirements :strips :typing)
  (:types elevator slow-elevator fast-elevator passenger count - object)
  
  (:predicates
    (at ?e - elevator ?c - count)
    (has ?e - elevator ?d - count)
    (can-hold ?e - elevator ?c - count)
    (reachable ?e - elevator ?c - count)
    (next-to ?c1 - count ?c2 - count)
    (above ?c1 - count ?c2 - count)
    (boarded ?p - passenger ?e - elevator)
    (passenger-count ?e - elevator ?d - count)
  )

  (:action move-slow-elevator
    :parameters (?e - slow-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action move-fast-elevator
    :parameters (?e - fast-elevator ?from - count ?to - count)
    :precondition (and (at ?e ?from) (above ?from ?to) (reachable ?e ?to))
    :effect (and (not (at ?e ?from)) (at ?e ?to))
  )

  (:action board-passenger
    :parameters (?p - passenger ?e - elevator ?c - count ?d - count ?e - count)
    :precondition (and (at ?e ?c) (at ?p ?c) (passenger-count ?e ?d) (next-to ?d ?e) (can-hold ?e ?e))
    :effect (and (boarded ?p ?e) (not (at ?p ?c)) (not (passenger-count ?e ?d)) (passenger-count ?e ?e))
  )

  (:action leave-elevator
    :parameters (?p - passenger ?e - elevator ?c - count ?d - count ?e - count)
    :precondition (and (at ?e ?c) (boarded ?p ?e) (passenger-count ?e ?d) (next-to ?e ?d))
    :effect (and (not (boarded ?p ?e)) (at ?p ?c) (not (passenger-count ?e ?d)) (passenger-count ?e ?e))
  )
)