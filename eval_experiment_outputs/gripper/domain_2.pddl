(define (domain gripper)
  (:requirements :strips :typing)

  (:types
    gripper object robot room - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (free ?r - robot ?g - gripper)
    (carrying ?r - robot ?o - object ?g - gripper)
    (at-obj ?o - object ?l - room)
  )

  (:action move
    :parameters (?a - robot ?b - room ?c - room)
    :precondition (at ?a ?b)
    :effect (and (not (at ?a ?b)) (at ?a ?c))
  )

  (:action pick
    :parameters (?a - robot ?b - object ?d - gripper ?c - room)
    :precondition (and (at-obj ?b ?c) (at ?a ?c) (free ?a ?d))
    :effect (and (not (at-obj ?b ?c)) (not (free ?a ?d)) (carrying ?a ?b ?d))
  )

  (:action drop
    :parameters (?a - robot ?b - object ?d - gripper ?c - room)
    :precondition (and (carrying ?a ?b ?d) (at ?a ?c))
    :effect (and (not (carrying ?a ?b ?d)) (at-obj ?b ?c) (free ?a ?d))
  )

)