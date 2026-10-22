(define (domain blocksworld_scaled)
  (:requirements :strips :typing)

  (:types
    object table - object
  )

  (:predicates
    (on ?a - object ?b - object)
    (clear ?a - object)
    (holding ?a - object)
    (hand-empty)
    (on-table ?a - object)
  )

  (:action pick-up
    :parameters (?a - object)
    :precondition (and (clear ?a) (on-table ?a) (hand-empty))
    :effect (and (holding ?a) (not (clear ?a)) (not (on-table ?a)) (not (hand-empty)))
  )

  (:action put-down
    :parameters (?a - object)
    :precondition (holding ?a)
    :effect (and (clear ?a) (on-table ?a) (hand-empty) (not (holding ?a)))
  )

  (:action stack
    :parameters (?a - object ?b - object)
    :precondition (and (clear ?b) (holding ?a))
    :effect (and (hand-empty) (clear ?a) (on ?a ?b) (not (clear ?b)) (not (holding ?a)))
  )

  (:action unstack
    :parameters (?a - object ?b - object)
    :precondition (and (on ?a ?b) (clear ?a) (hand-empty))
    :effect (and (holding ?a) (clear ?b) (not (on ?a ?b)) (not (clear ?a)) (not (hand-empty)))
  )

)