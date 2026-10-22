(define (domain robot_exploration)
  (:requirements :strips :typing)

  (:types
    doorway key payload robot room - object
  )

  (:predicates
    (at ?r - robot ?l - room)
    (connected ?d - doorway ?from - room ?to - room)
    (locked ?d - doorway)
    (has_key ?r - robot ?k - key)
    (key_shape ?k - key ?shape - object)
    (key_fits ?k - key ?d - doorway)
    (on_floor ?k - key ?l - room)
    (arm_free ?r - robot)
    (carrying ?r - robot ?p - payload)
    (in_room ?p - payload ?l - room)
  )

  (:action move
    :parameters (?r - robot ?from - room ?to - room ?d - doorway)
    :precondition (and (at ?r ?from) (connected ?d ?from ?to) (not (locked ?d)))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action pickup_key
    :parameters (?r - robot ?k - key ?l - room)
    :precondition (and (at ?r ?l) (on_floor ?k ?l) (arm_free ?r))
    :effect (and (not (on_floor ?k ?l)) (not (arm_free ?r)) (has_key ?r ?k))
  )

  (:action unlock_door
    :parameters (?r - robot ?d - doorway ?k - key)
    :precondition (and (has_key ?r ?k) (key_fits ?k ?d) (locked ?d))
    :effect (not (locked ?d))
  )

  (:action deposit_key
    :parameters (?r - robot ?k - key ?l - room)
    :precondition (and (at ?r ?l) (has_key ?r ?k))
    :effect (and (not (has_key ?r ?k)) (arm_free ?r) (on_floor ?k ?l))
  )

  (:action pickup_payload
    :parameters (?r - robot ?p - payload ?l - room)
    :precondition (and (at ?r ?l) (in_room ?p ?l) (arm_free ?r))
    :effect (and (not (in_room ?p ?l)) (not (arm_free ?r)) (carrying ?r ?p))
  )

  (:action deposit_payload
    :parameters (?r - robot ?p - payload ?l - room)
    :precondition (and (at ?r ?l) (carrying ?r ?p))
    :effect (and (not (carrying ?r ?p)) (arm_free ?r) (in_room ?p ?l))
  )

)