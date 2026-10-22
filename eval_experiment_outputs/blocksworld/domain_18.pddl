(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block table - object
  )

  (:predicates
    (on-table ?b - block)
    (on ?b1 - block ?b2 - block)
    (clear ?b - block)
    (holding ?b - block)
    (hand-empty)
  )

  (:action pick-up
    :parameters (?b - block)
    :precondition (and (on-table ?b) (clear ?b) (hand-empty))
    :effect (and (not (on-table ?b)) (not (clear ?b)) (not (hand-empty)) (holding ?b))
  )

  (:action unstack
    :parameters (?b1 - block ?b2 - block)
    :precondition (and (on ?b1 ?b2) (clear ?b1) (hand-empty))
    :effect (and (not (on ?b1 ?b2)) (clear ?b2) (not (hand-empty)) (holding ?b1))
  )

  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (on-table ?b) (clear ?b) (hand-empty) (not (holding ?b)))
  )

  (:action stack
    :parameters (?b1 - block ?b2 - block)
    :precondition (and (holding ?b1) (clear ?b2))
    :effect (and (on ?b1 ?b2) (not (clear ?b2)) (hand-empty) (not (holding ?b1)))
  )

)