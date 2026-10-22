(define (domain blocks_world)
  (:requirements :strips :typing)

  (:types
    arm block table - object
  )

  (:predicates
    (on ?b1 - block ?b2 - block)
    (ontable ?b - block ?t - table)
    (clear ?b - block)
    (holding ?a - arm ?b - block)
    (empty ?a - arm)
  )

  (:action pickup
    :parameters (?a - arm ?b - block ?t - table)
    :precondition (and (ontable ?b ?t) (clear ?b) (empty ?a))
    :effect (and (holding ?a ?b) (not (ontable ?b ?t)) (not (clear ?b)) (not (empty ?a)))
  )

  (:action putdown
    :parameters (?a - arm ?b - block ?t - table)
    :precondition (holding ?a ?b)
    :effect (and (ontable ?b ?t) (clear ?b) (empty ?a) (not (holding ?a ?b)))
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