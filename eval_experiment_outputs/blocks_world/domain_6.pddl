(define (domain blocks_world)
  (:requirements :strips :typing)

  (:types
    arm block table - object
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
    :precondition (and (empty ?a) (on_table ?b) (clear ?b))
    :effect (and (not (empty ?a)) (not (on_table ?b)) (not (clear ?b)) (holding ?a ?b))
  )

  (:action putdown
    :parameters (?a - arm ?b - block)
    :precondition (holding ?a ?b)
    :effect (and (empty ?a) (on_table ?b) (clear ?b) (not (holding ?a ?b)))
  )

  (:action stack
    :parameters (?a - arm ?b1 - block ?b2 - block)
    :precondition (and (holding ?a ?b1) (clear ?b2))
    :effect (and (empty ?a) (on ?b1 ?b2) (not (clear ?b2)) (not (holding ?a ?b1)))
  )

  (:action unstack
    :parameters (?a - arm ?b1 - block ?b2 - block)
    :precondition (and (empty ?a) (on ?b1 ?b2) (clear ?b1))
    :effect (and (holding ?a ?b1) (clear ?b2) (not (on ?b1 ?b2)) (not (empty ?a)))
  )

)