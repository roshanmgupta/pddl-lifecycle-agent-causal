(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    door key payload robot room string - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (connected ?from - room ?to - room ?d - door)
    (locked ?d - door)
    (key_shape ?k - key ?s - string)
    (holding_key ?r - robot ?k - key)
    (holding_payload ?r - robot ?p - payload)
    (key_in_room ?k - key ?l - room)
    (payload_in_room ?p - payload ?l - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?d - door)
    :precondition (and (at ?r ?from) (connected ?from ?to ?d) (not (locked ?d)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?l - room)
    :precondition (and (at ?r ?l) (key_in_room ?k ?l) (not (holding_key ?r ?k)) (not (holding_payload ?r ?p)))
    :effect (and (holding_key ?r ?k) (not (key_in_room ?k ?l)))
  )

  (:action unlock_door
    :parameters (?r - robot ?d - door ?k - key)
    :precondition (and (holding_key ?r ?k) (locked ?d))
    :effect (not (locked ?d))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?l - room)
    :precondition (and (at ?r ?l) (holding_key ?r ?k))
    :effect (and (not (holding_key ?r ?k)) (key_in_room ?k ?l))
  )

  (:action deposit_payload
    :parameters (?r - robot ?p - payload ?l - room)
    :precondition (and (at ?r ?l) (holding_payload ?r ?p))
    :effect (and (not (holding_payload ?r ?p)) (payload_in_room ?p ?l))
  )

  (:action pickup_payload
    :parameters (?r - robot ?p - payload ?l - room)
    :precondition (and (at ?r ?l) (payload_in_room ?p ?l) (not (holding_payload ?r ?p)) (not (holding_key ?r ?k)))
    :effect (and (holding_payload ?r ?p) (not (payload_in_room ?p ?l)))
  )

)