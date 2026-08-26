(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block - object
  )

  (:predicates
    (on ?b - block ?c - block)
    (ontable ?b - block)
    (clear ?b - block)
    (holding ?b - block)
    (handempty)
  )

  (:action pickup
    :parameters (?b - block)
    :precondition (and (ontable ?b) (clear ?b) (handempty))
    :effect (and (holding ?b) (not (ontable ?b)) (not (clear ?b)) (not (handempty)))
  )

  (:action putdown
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (ontable ?b) (clear ?b) (handempty) (not (holding ?b)))
  )

  (:action stack
    :parameters (?b - block ?c - block)
    :precondition (and (holding ?b) (clear ?c))
    :effect (and (on ?b ?c) (clear ?b) (handempty) (not (holding ?b)) (not (clear ?c)))
  )

  (:action unstack
    :parameters (?b - block ?c - block)
    :precondition (and (on ?b ?c) (clear ?b) (handempty))
    :effect (and (holding ?b) (clear ?c) (not (on ?b ?c)) (not (clear ?b)) (not (handempty)))
  )

)