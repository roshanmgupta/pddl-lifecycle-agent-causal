(define (domain warehouse_robot)
  (:requirements :strips :typing)

  (:types
    ball gripper robot room - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (connected ?l1 - room ?l2 - room)
    (in ?b - ball ?l - room)
    (holding ?r - robot ?g - gripper ?b - ball)
    (empty ?g - gripper)
  )

  (:action move_robot
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (and (at ?r ?from) (connected ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pick_up_ball
    :parameters (?r - robot ?g - gripper ?b - ball ?l - room)
    :precondition (and (at ?r ?l) (in ?b ?l) (empty ?g))
    :effect (and (holding ?r ?g ?b) (not (empty ?g)) (not (in ?b ?l)))
  )

  (:action release_ball
    :parameters (?r - robot ?g - gripper ?b - ball ?l - room)
    :precondition (and (at ?r ?l) (holding ?r ?g ?b))
    :effect (and (in ?b ?l) (empty ?g) (not (holding ?r ?g ?b)))
  )

)