(define (domain gripper_domain)
  (:requirements :strips :typing)

  (:types
    ball robot room - object
  )

  (:predicates
    (at-robot ?r - robot ?ro - room)
    (at-ball ?b - ball ?ro - room)
    (holding ?r - robot ?b - ball)
    (clean ?ro - room)
  )

  (:action pick
    :parameters (?r - robot ?b - ball ?ro - room)
    :precondition (and (at-robot ?r ?ro) (at-ball ?b ?ro) (not (holding ?r ?b)))
    :effect (and (holding ?r ?b) (not (at-ball ?b ?ro)))
  )

  (:action drop
    :parameters (?r - robot ?b - ball ?ro - room)
    :precondition (and (at-robot ?r ?ro) (holding ?r ?b))
    :effect (and (not (holding ?r ?b)) (at-ball ?b ?ro))
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at-robot ?r ?from)
    :effect (and (not (at-robot ?r ?from)) (at-robot ?r ?to))
  )

  (:action clean-room
    :parameters (?r - robot ?ro - room)
    :precondition (at-robot ?r ?ro)
    :effect (clean ?ro)
  )

)