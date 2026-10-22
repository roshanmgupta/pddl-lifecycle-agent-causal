(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (clear ?x - block)
    (holding ?x - block)
    (ontable ?x - block)
    (arm-empty)
  )

  (:action pick-up
    :parameters (?b - block)
    :precondition (and (ontable ?b) (clear ?b) (arm-empty))
    :effect (and (not (ontable ?b)) (not (clear ?b)) (holding ?b) (not (arm-empty)))
  )

  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (not (holding ?b)) (ontable ?b) (clear ?b) (arm-empty))
  )

  (:action stack
    :parameters (?b - block ?target - block)
    :precondition (and (holding ?b) (clear ?target))
    :effect (and (not (holding ?b)) (on ?b ?target) (not (clear ?target)))
  )

  (:action unstack
    :parameters (?b - block ?source - block)
    :precondition (and (on ?b ?source) (clear ?b) (arm-empty))
    :effect (and (not (on ?b ?source)) (holding ?b) (not (clear ?b)) (arm-empty) (clear ?source))
  )

)