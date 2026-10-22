(define (domain blocks_world)
  (:requirements :strips :typing)

  (:types
    arm block - object
  )

  (:predicates
    (on ?b1 - block ?b2 - block)
    (on_table ?b - block)
    (clear ?b - block)
    (holding ?a - arm ?b - block)
    (empty ?a - arm)
  )

  (:action pickup
    :parameters (?a - arm ?b - block)
    :precondition (and (on_table ?b) (clear ?b) (empty ?a))
    :effect (and (not (on_table ?b)) (not (clear ?b)) (not (empty ?a)) (holding ?a ?b))
  )

  (:action putdown
    :parameters (?a - arm ?b - block)
    :precondition (holding ?a ?b)
    :effect (and (on_table ?b) (clear ?b) (empty ?a) (not (holding ?a ?b)))
  )

  (:action stack
    :parameters (?a - arm ?b1 - block ?b2 - block)
    :precondition (and (holding ?a ?b1) (clear ?b2))
    :effect (and (on ?b1 ?b2) (clear ?b1) (empty ?a) (not (holding ?a ?b1)) (not (clear ?b2)))
  )

  (:action unstack
    :parameters (?a - arm ?b1 - block ?b2 - block)
    :precondition (and (on ?b1 ?b2) (clear ?b1) (empty ?a))
    :effect (and (holding ?a ?b1) (clear ?b2) (not (on ?b1 ?b2)) (not (clear ?b1)) (not (empty ?a)))
  )

)