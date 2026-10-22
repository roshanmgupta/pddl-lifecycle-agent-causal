(define (domain robot_gripper_domain)
  (:requirements :strips :typing)

  (:types
    ball gripper robot room - object
  )

  (:predicates
    (at ?r - robot ?ro - room)
    (empty ?g - gripper)
    (holding ?r - robot ?g - gripper ?b - ball)
    (in ?b - ball ?ro - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pick
    :parameters (?r - robot ?g - gripper ?b - ball ?ro - room)
    :precondition (and (at ?r ?ro) (empty ?g) (in ?b ?ro))
    :effect (and (not (empty ?g)) (not (in ?b ?ro)) (holding ?r ?g ?b))
  )

  (:action drop
    :parameters (?r - robot ?g - gripper ?b - ball ?ro - room)
    :precondition (and (at ?r ?ro) (holding ?r ?g ?b))
    :effect (and (empty ?g) (in ?b ?ro) (not (holding ?r ?g ?b)))
  )

)