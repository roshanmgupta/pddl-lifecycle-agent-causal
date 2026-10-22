(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key payload robot room string - object
  )

  (:predicates
    (at ?r - robot ?rm - room)
    (connected ?rm1 - room ?rm2 - room)
    (locked ?d - door)
    (has_key ?r - robot ?k - key)
    (key_shape ?k - key ?shape - string)
    (key_fits ?k - key ?d - door)
    (free_arm ?r - robot)
    (carrying ?r - robot ?p - payload)
    (key_in_room ?k - key ?rm - room)
    (payload_in_room ?p - payload ?rm - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?d - door)
    :precondition (and (at ?r ?from) (connected ?from ?to) (not (locked ?d)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (key_in_room ?k ?rm) (free_arm ?r))
    :effect (and (has_key ?r ?k) (not (key_in_room ?k ?rm)) (not (free_arm ?r)))
  )

  (:action unlock_door
    :parameters (?r - robot ?k - key ?d - door ?rm1 - room ?rm2 - room)
    :precondition (and (has_key ?r ?k) (key_fits ?k ?d) (locked ?d) (connected ?rm1 ?rm2) (at ?r ?rm1))
    :effect (not (locked ?d))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (has_key ?r ?k) (at ?r ?rm))
    :effect (and (not (has_key ?r ?k)) (key_in_room ?k ?rm) (free_arm ?r))
  )

  (:action pickup_payload
    :parameters (?r - robot ?p - payload ?rm - room)
    :precondition (and (at ?r ?rm) (payload_in_room ?p ?rm) (free_arm ?r))
    :effect (and (carrying ?r ?p) (not (payload_in_room ?p ?rm)) (not (free_arm ?r)))
  )

  (:action deposit_payload
    :parameters (?r - robot ?p - payload ?rm - room)
    :precondition (and (carrying ?r ?p) (at ?r ?rm))
    :effect (and (not (carrying ?r ?p)) (payload_in_room ?p ?rm) (free_arm ?r))
  )

)