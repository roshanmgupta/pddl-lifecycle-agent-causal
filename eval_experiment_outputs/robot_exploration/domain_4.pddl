(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key robot room string - object
  )

  (:predicates
    (at ?r - robot ?rm - room)
    (connected ?rm1 - room ?rm2 - room)
    (locked ?d - door)
    (unlocked ?d - door)
    (has_key ?r - robot ?k - key)
    (key_shape ?k - key ?shape - string)
    (door_shape ?d - door ?shape - string)
    (key_at ?k - key ?rm - room)
    (arm_free ?r - robot)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (and (at ?r ?from) (connected ?from ?to) (not (locked ?d - door)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (key_at ?k ?rm) (arm_free ?r))
    :effect (and (not (key_at ?k ?rm)) (has_key ?r ?k) (not (arm_free ?r)))
  )

  (:action unlock_door
    :parameters (?r - robot ?d - door ?k - key)
    :precondition (and (has_key ?r ?k) (key_shape ?k ?shape) (door_shape ?d ?shape) (locked ?d))
    :effect (and (not (locked ?d)) (unlocked ?d))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (has_key ?r ?k))
    :effect (and (not (has_key ?r ?k)) (key_at ?k ?rm) (arm_free ?r))
  )

)