(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    block robot - object
  )

  (:predicates
    (on ?x - block ?y - block)
    (on-table ?x - block)
    (clear ?x - block)
    (holding ?r - robot ?x - block)
    (hand-empty ?r - robot)
  )

  (:action pick-up
    :parameters (?r - robot ?b - block)
    :precondition (and (hand-empty ?r) (on-table ?b) (clear ?b))
    :effect (and (not (hand-empty ?r)) (not (on-table ?b)) (not (clear ?b)) (holding ?r ?b))
  )

  (:action put-down
    :parameters (?r - robot ?b - block)
    :precondition (holding ?r ?b)
    :effect (and (not (holding ?r ?b)) (hand-empty ?r) (on-table ?b) (clear ?b))
  )

  (:action stack
    :parameters (?r - robot ?b1 - block ?b2 - block)
    :precondition (and (holding ?r ?b1) (clear ?b2))
    :effect (and (not (holding ?r ?b1)) (not (clear ?b2)) (on ?b1 ?b2))
  )

  (:action unstack
    :parameters (?r - robot ?b1 - block ?b2 - block)
    :precondition (and (hand-empty ?r) (clear ?b1) (on ?b1 ?b2))
    :effect (and (not (on ?b1 ?b2)) (holding ?r ?b1) (clear ?b2) (not (hand-empty ?r)))
  )

)