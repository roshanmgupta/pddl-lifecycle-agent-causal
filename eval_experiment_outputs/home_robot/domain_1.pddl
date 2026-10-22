(define (domain home_robot)
  (:requirements :strips :typing)

  (:types
    gripper location object robot - object
  )

  (:predicates
    (at ?r - robot ?l - location)
    (at ?o - object ?l - location)
    (holding ?r - robot ?o - object)
    (gripper-empty ?r - robot)
    (connected ?l1 - location ?l2 - location)
  )

  (:action move
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (and (at ?r ?from) (connected ?from ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pick-up
    :parameters (?r - robot ?o - object ?l - location)
    :precondition (and (at ?r ?l) (at ?o ?l) (gripper-empty ?r))
    :effect (and (not (at ?o ?l)) (not (gripper-empty ?r)) (holding ?r ?o))
  )

  (:action put-down
    :parameters (?r - robot ?o - object ?l - location)
    :precondition (and (at ?r ?l) (holding ?r ?o))
    :effect (and (not (holding ?r ?o)) (gripper-empty ?r) (at ?o ?l))
  )

)