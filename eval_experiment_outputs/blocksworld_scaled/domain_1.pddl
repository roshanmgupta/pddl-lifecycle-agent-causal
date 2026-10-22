(define (domain blocksworld_scaled)
  (:requirements :strips :typing)

  (:types
    block table - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (on-table ?x - block)
    (clear ?x - block)
    (holding ?x - block)
    (hand-empty)
  )

  (:action pick-up
    :parameters (?a - block)
    :precondition (and (on-table ?a) (clear ?a) (hand-empty))
    :effect (and (holding ?a) (not (on-table ?a)) (not (clear ?a)) (not (hand-empty)))
  )

  (:action put-down
    :parameters (?a - block)
    :precondition (holding ?a)
    :effect (and (on-table ?a) (clear ?a) (hand-empty) (not (holding ?a)))
  )

  (:action stack
    :parameters (?a - block ?b - block)
    :precondition (and (holding ?a) (clear ?b))
    :effect (and (on ?a ?b) (clear ?a) (hand-empty) (not (holding ?a)) (not (clear ?b)))
  )

  (:action unstack
    :parameters (?a - block ?b - block)
    :precondition (and (on ?a ?b) (clear ?a) (hand-empty))
    :effect (and (holding ?a) (clear ?b) (not (on ?a ?b)) (not (clear ?a)) (not (hand-empty)))
  )

)