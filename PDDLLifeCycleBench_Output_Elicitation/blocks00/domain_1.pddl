(define (domain blocks00)
  (:requirements :strips :typing)

  (:types
    object - object
  )

  (:predicates
    (clear ?x - object)
    (on ?x - object ?y - object)
    (on-table ?x - object)
    (holding ?x - object)
    (hand-empty)
  )

  (:action pick-up
    :parameters (?a - object)
    :precondition (and (clear ?a) (on-table ?a) (hand-empty))
    :effect (and (holding ?a) (not (on-table ?a)) (not (clear ?a)) (not (hand-empty)))
  )

  (:action put-down
    :parameters (?a - object)
    :precondition (holding ?a)
    :effect (and (clear ?a) (on-table ?a) (not (holding ?a)) (hand-empty))
  )

  (:action stack
    :parameters (?a - object ?b - object)
    :precondition (and (holding ?a) (clear ?b))
    :effect (and (clear ?a) (not (holding ?a)) (on ?a ?b) (not (clear ?b)) (hand-empty))
  )

  (:action unstack
    :parameters (?a - object ?b - object)
    :precondition (and (on ?a ?b) (clear ?a) (hand-empty))
    :effect (and (holding ?a) (clear ?b) (not (clear ?a)) (not (hand-empty)) (not (on ?a ?b)))
  )

)