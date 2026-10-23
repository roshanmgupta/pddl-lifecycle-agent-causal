(define (domain gripper)
  (:requirements :strips)
  (:predicates
    (at ?robot ?room)
    (free-from ?robot ?gripper)
    (carrying ?robot ?object ?gripper)
    (at-object ?object ?room)
  )
  (:action move
    :parameters (?robot ?from ?to)
    :precondition (at ?robot ?from)
    :effect (and
      (at ?robot ?to)
      (not (at ?robot ?from))
    )
  )
  (:action pick
    :parameters (?robot ?object ?gripper ?room)
    :precondition (and
      (at-object ?object ?room)
      (at ?robot ?room)
      (free-from ?robot ?gripper)
    )
    :effect (and
      (carrying ?robot ?object ?gripper)
      (not (at-object ?object ?room))
      (not (free-from ?robot ?gripper))
    )
  )
  (:action drop
    :parameters (?robot ?object ?gripper ?room)
    :precondition (and
      (carrying ?robot ?object ?gripper)
      (at ?robot ?room)
    )
    :effect (and
      (at-object ?object ?room)
      (free-from ?robot ?gripper)
      (not (carrying ?robot ?object ?gripper))
    )
  )
)