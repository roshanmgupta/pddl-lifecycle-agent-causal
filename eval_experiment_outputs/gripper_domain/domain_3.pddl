(define (domain gripper_domain)
  (:requirements :strips :typing)

  (:types
    ball robby room - object
  )

  (:predicates
    (at-robby ?r - robby ?l - room)
    (at-ball ?b - ball ?l - room)
    (carry ?r - robby ?b - ball)
    (clean ?l - room)
  )

  (:action pick
    :parameters (?r - robby ?b - ball ?l - room)
    :precondition (and (at-robby ?r ?l) (at-ball ?b ?l) (not (carry ?r ?b)))
    :effect (and (not (at-ball ?b ?l)) (carry ?r ?b))
  )

  (:action drop
    :parameters (?r - robby ?b - ball ?l - room)
    :precondition (and (at-robby ?r ?l) (carry ?r ?b))
    :effect (and (not (carry ?r ?b)) (at-ball ?b ?l))
  )

  (:action move
    :parameters (?r - robby ?from - room ?to - room)
    :precondition (at-robby ?r ?from)
    :effect (and (not (at-robby ?r ?from)) (at-robby ?r ?to))
  )

  (:action clean-room
    :parameters (?r - robby ?l - room)
    :precondition (at-robby ?r ?l)
    :effect (clean ?l)
  )

)