(define (domain gripper)
  (:requirements :strips :typing)

  (:types
    gripper robot room - object
  )

  (:predicates
    (at ?b - object ?loc - room)
    (free-from ?r - robot ?g - gripper)
    (carrying ?r - robot ?b - object ?g - gripper)
  )

  (:action move_robot
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (at ?r ?to) (not (at ?r ?from)))
  )

  (:action pick_object
    :parameters (?r - robot ?b - object ?g - gripper ?loc - room)
    :precondition (and (at ?b ?loc) (at ?r ?loc) (free-from ?r ?g))
    :effect (and (carrying ?r ?b ?g) (not (at ?b ?loc)) (not (free-from ?r ?g)))
  )

  (:action drop_object
    :parameters (?r - robot ?b - object ?g - gripper ?loc - room)
    :precondition (and (carrying ?r ?b ?g) (at ?r ?loc))
    :effect (and (at ?b ?loc) (free-from ?r ?g) (not (carrying ?r ?b ?g)))
  )

)