(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key payload robot room string - object
  )

  (:predicates
    (at ?r - robot ?rm - room)
    (connected ?rm1 - room ?rm2 - room)
    (locked ?d - door)
    (unlocked ?d - door)
    (has_key ?r - robot ?k - key)
    (key_shape ?k - key ?shape - string)
    (key_in_room ?k - key ?rm - room)
    (arm_free ?r - robot)
    (carrying ?r - robot ?p - payload)
    (payload_in_room ?p - payload ?rm - room)
    (door_between ?d - door ?rm1 - room ?rm2 - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?d - door)
    :precondition (and (at ?r ?from) (connected ?from ?to) (door_between ?d ?from ?to) (not (locked ?d)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (key_in_room ?k ?rm) (arm_free ?r))
    :effect (and (has_key ?r ?k) (not (key_in_room ?k ?rm)) (not (arm_free ?r)))
  )

  (:action unlock_door
    :parameters (?r - robot ?d - door ?k - key)
    :precondition (and (has_key ?r ?k) (locked ?d))
    :effect (and (unlocked ?d) (not (locked ?d)))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (has_key ?r ?k))
    :effect (and (key_in_room ?k ?rm) (not (has_key ?r ?k)) (arm_free ?r))
  )

  (:action deposit_payload
    :parameters (?r - robot ?p - payload ?rm - room)
    :precondition (and (at ?r ?rm) (carrying ?r ?p))
    :effect (and (payload_in_room ?p ?rm) (not (carrying ?r ?p)) (arm_free ?r))
  )

  (:action pickup_payload
    :parameters (?r - robot ?p - payload ?rm - room)
    :precondition (and (at ?r ?rm) (payload_in_room ?p ?rm) (arm_free ?r))
    :effect (and (carrying ?r ?p) (not (payload_in_room ?p ?rm)) (not (arm_free ?r)))
  )

)