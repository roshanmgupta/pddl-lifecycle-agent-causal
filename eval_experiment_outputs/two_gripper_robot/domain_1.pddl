(define (domain two_gripper_robot)
  (:requirements :strips :typing)

  (:types
    gripper robot room spherical_object - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (free ?r - robot ?g - gripper)
    (carrying ?r - robot ?o - spherical_object ?g - gripper)
    (at_obj ?o - spherical_object ?l - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pick
    :parameters (?r - robot ?o - spherical_object ?g - gripper ?l - room)
    :precondition (and (at_obj ?o ?l) (at ?r ?l) (free ?r ?g))
    :effect (and (not (at_obj ?o ?l)) (not (free ?r ?g)) (carrying ?r ?o ?g))
  )

  (:action drop
    :parameters (?r - robot ?o - spherical_object ?g - gripper ?l - room)
    :precondition (and (carrying ?r ?o ?g) (at ?r ?l))
    :effect (and (not (carrying ?r ?o ?g)) (at_obj ?o ?l) (free ?r ?g))
  )

)