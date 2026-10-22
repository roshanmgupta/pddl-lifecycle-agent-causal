(define (domain warehouse_robot)
  (:requirements :strips :typing)

  (:types
    ball gripper robot room - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (connected ?from - room ?to - room)
    (in ?b - ball ?l - room)
    (empty ?g - gripper)
    (holding ?g - gripper ?b - ball)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (and (at ?r ?from) (connected ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pick
    :parameters (?r - robot ?b - ball ?l - room ?g - gripper)
    :precondition (and (at ?r ?l) (in ?b ?l) (empty ?g))
    :effect (and (not (in ?b ?l)) (not (empty ?g)) (holding ?g ?b))
  )

  (:action release
    :parameters (?r - robot ?b - ball ?l - room ?g - gripper)
    :precondition (and (at ?r ?l) (holding ?g ?b))
    :effect (and (in ?b ?l) (empty ?g) (not (holding ?g ?b)))
  )

)