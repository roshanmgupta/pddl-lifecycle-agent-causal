(define (domain BLOCKSWORLD)
  (:requirements :strips :typing)

  (:types
    block robotic-arm table - object
  )

  (:predicates
    (on-table ?b - block)
    (clear ?b - block)
    (arm-empty ?a - robotic-arm)
    (on-block ?b1 - block ?b2 - block)
  )

  (:action pick-up
    :parameters (?a - robotic-arm ?b - block)
    :precondition (and (clear ?b) (arm-empty ?a))
    :effect (and (not (clear ?b)) (not (arm-empty ?a)))
  )

  (:action put-down
    :parameters (?a - robotic-arm ?b - block)
    :precondition (not (arm-empty ?a))
    :effect (and (clear ?b) (arm-empty ?a))
  )

  (:action stack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (clear ?b2) (not (clear ?b1)) (not (arm-empty ?a)))
    :effect (and (on-block ?b1 ?b2) (clear ?b1) (arm-empty ?a))
  )

  (:action unstack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (on-block ?b1 ?b2) (arm-empty ?a))
    :effect (and (not (on-block ?b1 ?b2)) (clear ?b2) (not (clear ?b1)) (not (arm-empty ?a)))
  )

)