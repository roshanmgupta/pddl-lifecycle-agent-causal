(define (domain visitall)
  (:requirements :strips)
  (:predicates
    (at ?loc)
    (visited ?loc)
    (connected ?loc1 ?loc2)
  )
  (:action move
    :parameters (?from ?to)
    :precondition (and (at ?from) (connected ?from ?to))
    :effect (and
      (not (at ?from))
      (at ?to)
      (visited ?to)
    )
  )
)