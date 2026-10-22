(define (domain block_stacking)
  (:requirements One cannot place more than one block on another block. b5 is on top of b3. b4 is on top of b2. b2 is on top of b1. b3 is on top of b4. b1 is on the table. b5 is clear.)

  (:types
    block location - object
  )

  (:predicates
    (at ?r - block ?l - location)
    (on ?x - block ?y - block)
    (clear ?l - location)
  )

  (:action stack
    :parameters (?r - block ?target - block ?from - location ?to - location)
    :precondition (and (at ?r ?from) (not (on ?r ?target)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

)