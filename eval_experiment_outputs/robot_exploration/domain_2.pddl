(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key payload robot room - object
  )

  (:predicates
    (at ?r - robot ?rm - room)
    (connected ?rm1 - room ?rm2 - room ?d - door)
    (locked ?d - door)
    (key_shape ?k - key ?d - door)
    (holding_key ?r - robot ?k - key)
    (holding_payload ?r - robot ?p - payload)
    (key_at ?k - key ?rm - room)
    (payload_at ?p - payload ?rm - room)
    (handempty ?r - robot)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?d - door)
    :precondition (and (at ?r ?from) (connected ?from ?to ?d) (not (locked ?d)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (key_at ?k ?rm) (not (holding_key ?r ?k)) (handempty ?r))
    :effect (and (holding_key ?r ?k) (not (key_at ?k ?rm)) (not (handempty ?r)))
  )

  (:action unlock_door
    :parameters (?r - robot ?d - door ?k - key)
    :precondition (and (holding_key ?r ?k) (key_shape ?k ?d) (locked ?d))
    :effect (not (locked ?d))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?rm - room)
    :precondition (and (at ?r ?rm) (holding_key ?r ?k))
    :effect (and (key_at ?k ?rm) (not (holding_key ?r ?k)) (handempty ?r))
  )

  (:action deposit_payload
    :parameters (?r - robot ?p - payload ?rm - room)
    :precondition (and (at ?r ?rm) (holding_payload ?r ?p))
    :effect (and (payload_at ?p ?rm) (not (holding_payload ?r ?p)) (handempty ?r))
  )

)