(define (domain gripper98)
  (:requirements :strips :typing)

  (:types
    ball gripper room - object
  )

  (:predicates
    (is-room ?r - room)
    (is-ball ?b - ball)
    (is-gripper ?g - gripper)
    (robot-at ?r - room)
    (ball-at ?b - ball ?r - room)
    (gripper-free ?g - gripper)
    (carrying ?g - gripper ?b - ball)
  )

  (:action move
    :parameters (?from - room ?to - room)
    :precondition (and (is-room ?from) (is-room ?to) (robot-at ?from))
    :effect (and (robot-at ?to) (not (robot-at ?from)))
  )

  (:action pick
    :parameters (?b - ball ?r - room ?g - gripper)
    :precondition (and (is-ball ?b) (is-room ?r) (is-gripper ?g) (ball-at ?b ?r) (robot-at ?r) (gripper-free ?g))
    :effect (and (carrying ?g ?b) (not (ball-at ?b ?r)) (not (gripper-free ?g)))
  )

  (:action drop
    :parameters (?b - ball ?r - room ?g - gripper)
    :precondition (and (is-ball ?b) (is-room ?r) (is-gripper ?g) (carrying ?g ?b) (robot-at ?r))
    :effect (and (ball-at ?b ?r) (gripper-free ?g) (not (carrying ?g ?b)))
  )

)