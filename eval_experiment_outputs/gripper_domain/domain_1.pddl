(define (domain gripper_domain)
  (:requirements :strips :typing)

  (:types
    ball robby room - object
  )

  (:predicates
    (at ?r - robby ?l - room)
    (at ?b - ball ?l - room)
    (carry ?r - robby ?b - ball)
    (clean ?l - room)
  )

  (:action pick
    :parameters (?r - robby ?b - ball ?l - room)
    :precondition (and (at ?r ?l) (at ?b ?l) (not (carry ?r ?b)))
    :effect (and (not (at ?b ?l)) (carry ?r ?b))
  )

  (:action drop
    :parameters (?r - robby ?b - ball ?l - room)
    :precondition (and (at ?r ?l) (carry ?r ?b))
    :effect (and (not (carry ?r ?b)) (at ?b ?l))
  )

  (:action move
    :parameters (?r - robby ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action clean-room
    :parameters (?r - robby ?l - room)
    :precondition (at ?r ?l)
    :effect (clean ?l)
  )

)