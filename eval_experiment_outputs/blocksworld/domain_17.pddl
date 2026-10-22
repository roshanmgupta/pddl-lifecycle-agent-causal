(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block - object
  )

  (:predicates
    (clear ?x - block)
    (ontable ?x - block)
    (handempty)
    (holding ?x - block)
    (on ?x - block ?y - block)
  )

  (:action pick-up
    :parameters (?x - block)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (holding ?x) (not (clear ?x)) (not (ontable ?x)) (not (handempty)))
  )

  (:action put-down
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (clear ?x) (handempty) (ontable ?x) (not (holding ?x)))
  )

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (clear ?y) (holding ?x))
    :effect (and (handempty) (clear ?x) (on ?x ?y) (not (clear ?y)) (not (holding ?x)))
  )

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (on ?x ?y) (clear ?x) (handempty))
    :effect (and (holding ?x) (clear ?y) (not (on ?x ?y)) (not (clear ?x)) (not (handempty)))
  )

)