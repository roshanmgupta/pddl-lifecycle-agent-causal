(define (domain BLOCKSWORLD)
  (:requirements :strips)
  (:types block table robotic-arm)
  
  (:predicates
    (on-table ?b - block)
    (on-block ?b1 - block ?b2 - block)
    (clear ?b - block)
    (arm-empty ?a - robotic-arm)
  )

  (:action pick-up
    :parameters (?a - robotic-arm ?b - block)
    :precondition (and (clear ?b) (arm-empty ?a))
    :effect (and (not (clear ?b)) (not (arm-empty ?a)) (not (on-table ?b)))
  )

  (:action put-down
    :parameters (?a - robotic-arm ?b - block)
    :precondition (not (arm-empty ?a))
    :effect (and (clear ?b) (arm-empty ?a) (on-table ?b))
  )

  (:action stack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (not (arm-empty ?a)) (clear ?b2))
    :effect (and (not (clear ?b2)) (not (on-block ?b1 ?b2)) (on-block ?b1 ?b2) (clear ?b1))
  )

  (:action unstack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (clear ?b1) (not (arm-empty ?a)) (on-block ?b1 ?b2))
    :effect (and (clear ?b2) (not (on-block ?b1 ?b2)) (not (clear ?b1)))
  )
)