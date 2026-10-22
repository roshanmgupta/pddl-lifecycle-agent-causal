(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (on-table ?x - block)
    (clear ?x - block)
    (handempty)
    (holding ?x - block)
  )

  (:action pick-up
    :parameters (?b - block)
    :precondition (and (on-table ?b) (clear ?b) (handempty))
    :effect (and (not (on-table ?b)) (not (clear ?b)) (not (handempty)) (holding ?b))
  )

  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (not (holding ?b)) (on-table ?b) (clear ?b) (handempty))
  )

  (:action stack
    :parameters (?b - block ?c - block)
    :precondition (and (holding ?b) (clear ?c))
    :effect (and (not (holding ?b)) (not (clear ?c)) (on ?b ?c) (clear ?b) (handempty))
  )

  (:action unstack
    :parameters (?b - block ?c - block)
    :precondition (and (on ?b ?c) (clear ?b) (handempty))
    :effect (and (not (on ?b ?c)) (not (clear ?b)) (not (handempty)) (holding ?b) (clear ?c))
  )

)