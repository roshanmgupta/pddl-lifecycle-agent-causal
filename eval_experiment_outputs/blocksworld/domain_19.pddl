(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block robotic-arm table - object
  )

  (:predicates
    (on-table ?b - block)
    (on-block ?b1 - block ?b2 - block)
    (clear ?b - block)
    (arm-empty ?a - robotic-arm)
  )

  (:action pick-up
    :parameters (?a - robotic-arm ?b - block)
    :precondition (and (on-table ?b) (clear ?b) (arm-empty ?a))
    :effect (and (not (on-table ?b)) (not (clear ?b)) (not (arm-empty ?a)))
  )

  (:action put-down
    :parameters (?a - robotic-arm ?b - block)
    :precondition (not (arm-empty ?a))
    :effect (and (on-table ?b) (clear ?b) (arm-empty ?a))
  )

  (:action stack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (clear ?b2) (not (arm-empty ?a)))
    :effect (and (on-block ?b1 ?b2) (clear ?b1) (arm-empty ?a) (not (clear ?b2)))
  )

  (:action unstack
    :parameters (?a - robotic-arm ?b1 - block ?b2 - block)
    :precondition (and (on-block ?b1 ?b2) (clear ?b1) (arm-empty ?a))
    :effect (and (not (on-block ?b1 ?b2)) (not (clear ?b1)) (clear ?b2) (not (arm-empty ?a)))
  )

)