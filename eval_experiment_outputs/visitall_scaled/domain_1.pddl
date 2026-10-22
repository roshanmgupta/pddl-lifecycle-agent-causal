(define (domain visitall_scaled)
  (:requirements :strips :typing)

  (:types
    loc robot - object
  )

  (:predicates
    (at ?r - robot ?l - loc)
    (connected ?from - loc ?to - loc)
    (visited ?l - loc)
  )

  (:action move
    :parameters (?r - robot ?from - loc ?to - loc)
    :precondition (and (at ?r ?from) (connected ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to) (visited ?to))
  )

)