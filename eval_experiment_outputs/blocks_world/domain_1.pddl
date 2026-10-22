(define (domain blocks_world)
  (:requirements :strips :typing)

  (:types
    block table - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)
    (holding ?x - block)
    (arm-empty)
  )

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (not (holding ?x)) (arm-empty) (not (clear ?y)) (on ?x ?y) (clear ?x))
  )

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (on ?x ?y) (clear ?x) (arm-empty))
    :effect (and (holding ?x) (clear ?y) (not (on ?x ?y)) (not (clear ?x)) (not (arm-empty)))
  )

  (:action pickup
    :parameters (?x - block)
    :precondition (and (ontable ?x) (clear ?x) (arm-empty))
    :effect (and (holding ?x) (not (ontable ?x)) (not (clear ?x)) (not (arm-empty)))
  )

  (:action putdown
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (not (holding ?x)) (arm-empty) (ontable ?x) (clear ?x))
  )

)