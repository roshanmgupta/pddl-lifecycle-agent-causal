(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block table - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (clear ?x - block)
    (ontable ?x - block)
    (holding ?x - block)
    (arm-empty)
  )

  (:action pickup
    :parameters (?b - block)
    :precondition (and (ontable ?b) (clear ?b) (arm-empty))
    :effect (and (not (ontable ?b)) (not (arm-empty)) (holding ?b))
  )

  (:action putdown
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (not (holding ?b)) (ontable ?b) (arm-empty))
  )

  (:action stack
    :parameters (?b - block ?target - block)
    :precondition (and (holding ?b) (clear ?target))
    :effect (and (not (holding ?b)) (not (clear ?target)) (on ?b ?target))
  )

  (:action unstack
    :parameters (?b - block ?from - block)
    :precondition (and (on ?b ?from) (clear ?b) (arm-empty))
    :effect (and (not (on ?b ?from)) (not (arm-empty)) (holding ?b) (clear ?from))
  )

)