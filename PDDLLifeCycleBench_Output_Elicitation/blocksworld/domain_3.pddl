(define (domain blocksworld)
  (:requirements :strips :typing)

  (:types
    object - object
  )

  (:predicates
    (on-table ?x - object)
    (on ?x - object ?y - object)
    (clear ?x - object)
    (holding ?x - object)
    (hand-empty)
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