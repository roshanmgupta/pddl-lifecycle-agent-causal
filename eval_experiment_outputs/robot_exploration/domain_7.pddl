(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key robot room shape - object
  )

  (:predicates
    (at ?r - robot ?room - room)
    (connected ?room1 - room ?room2 - room ?door - door)
    (locked ?door - door)
    (key_shape ?key - key ?shape - shape)
    (has_key ?r - robot ?key - key)
    (free_arm ?r - robot)
    (key_in_room ?key - key ?room - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?door - door)
    :precondition (and (at ?r ?from) (connected ?from ?to ?door) (not (locked ?door)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?key - key ?room - room)
    :precondition (and (at ?r ?room) (key_in_room ?key ?room) (free_arm ?r))
    :effect (and (has_key ?r ?key) (not (key_in_room ?key ?room)) (not (free_arm ?r)))
  )

  (:action unlock_door
    :parameters (?r - robot ?door - door ?key - key ?shape - shape)
    :precondition (and (has_key ?r ?key) (locked ?door) (key_shape ?key ?shape))
    :effect (not (locked ?door))
  )

  (:action deposit_key
    :parameters (?r - robot ?key - key ?room - room)
    :precondition (and (at ?r ?room) (has_key ?r ?key))
    :effect (and (key_in_room ?key ?room) (not (has_key ?r ?key)) (free_arm ?r))
  )

)