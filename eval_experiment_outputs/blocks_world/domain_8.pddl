(define (domain blocks_world)
  (:requirements :strips :typing)

  (:types
    arm block - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (on-table ?x - block)
    (clear ?x - block)
    (holding ?a - arm ?x - block)
    (empty ?a - arm)
  )

  (:action pickup
    :parameters (?a - arm ?x - block)
    :precondition (and (empty ?a) (on-table ?x) (clear ?x))
    :effect (and (not (empty ?a)) (not (on-table ?x)) (not (clear ?x)) (holding ?a ?x))
  )

  (:action putdown
    :parameters (?a - arm ?x - block)
    :precondition (holding ?a ?x)
    :effect (and (empty ?a) (on-table ?x) (clear ?x) (not (holding ?a ?x)))
  )

  (:action stack
    :parameters (?a - arm ?x - block ?y - block)
    :precondition (and (holding ?a ?x) (clear ?y))
    :effect (and (empty ?a) (on ?x ?y) (clear ?x) (not (holding ?a ?x)) (not (clear ?y)))
  )

  (:action unstack
    :parameters (?a - arm ?x - block ?y - block)
    :precondition (and (empty ?a) (on ?x ?y) (clear ?x))
    :effect (and (holding ?a ?x) (clear ?y) (not (empty ?a)) (not (on ?x ?y)) (not (clear ?x)))
  )

)