(define (domain gripper_domain)
  (:requirements :strips :typing)

  (:types
    ball robby room - object
  )

  (:predicates
    (at-robby ?r - robby ?ro - room)
    (at-ball ?b - ball ?ro - room)
    (carry ?r - robby ?b - ball)
    (clean ?ro - room)
    (at ?b - ball ?ro - room)
  )

  (:action pick
    :parameters (?r - robby ?b - ball ?ro - room)
    :precondition (and (at-robby ?r ?ro) (at-ball ?b ?ro) (not (carry ?r ?b)))
    :effect (and (not (at-ball ?b ?ro)) (carry ?r ?b))
  )

  (:action drop
    :parameters (?r - robby ?b - ball ?ro - room)
    :precondition (and (at-robby ?r ?ro) (carry ?r ?b))
    :effect (and (not (carry ?r ?b)) (at-ball ?b ?ro))
  )

  (:action move
    :parameters (?r - robby ?from - room ?to - room)
    :precondition (at-robby ?r ?from)
    :effect (and (not (at-robby ?r ?from)) (at-robby ?r ?to))
  )

  (:action clean-room
    :parameters (?r - robby ?ro - room)
    :precondition (at-robby ?r ?ro)
    :effect (clean ?ro)
  )

)