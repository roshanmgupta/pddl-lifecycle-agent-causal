(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block table - object
  )

  (:predicates
    (on ?a - object ?b - object)
    (clear ?a - block)
    (holding ?a - block)
    (hand-empty)
  )

  (:action pick-up
    :parameters (?a - block)
    :precondition (and (clear ?a) (on ?a) (hand-empty))
    :effect (and (holding ?a) (not (clear ?a)) (not (on ?a)) (not (hand-empty)))
  )

  (:action put-down
    :parameters (?a - block)
    :precondition (holding ?a)
    :effect (and (clear ?a) (on ?a) (hand-empty) (not (holding ?a)))
  )

  (:action stack
    :parameters (?a - block ?b - block)
    :precondition (and (clear ?b) (holding ?a))
    :effect (and (clear ?a) (on ?a - ?b) (not (clear ?b)) (not (holding ?a)))
  )

  (:action unstack
    :parameters (?a - block ?b - block)
    :precondition (and (on ?a - ?b) (clear ?a) (hand-empty))
    :effect (and (holding ?a) (clear ?b) (not (on ?a - ?b)) (not (clear ?a)) (not (hand-empty)))
  )

)