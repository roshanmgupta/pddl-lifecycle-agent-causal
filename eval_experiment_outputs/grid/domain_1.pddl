(define (domain grid)
  (:requirements :strips :typing)

  (:types
    key place robot shape - object
  )

  (:predicates
    (connected ?a - place ?b - place)
    (has-shape ?k - key ?s - shape)
    (has-lock-shape ?p - place ?s - shape)
    (locked ?p - place)
    (open ?p - place)
    (at-robot ?r - robot ?p - place)
    (holding ?r - robot ?k - key)
    (arm-empty ?r - robot)
    (at-key ?k - key ?p - place)
  )

  (:action unlock
    :parameters (?r - robot ?a - place ?b - place ?k - key ?s - shape)
    :precondition (and (connected ?a ?b) (has-shape ?k ?s) (has-lock-shape ?b ?s) (at-robot ?r ?a) (locked ?b) (holding ?r ?k))
    :effect (and (open ?b) (not (locked ?b)))
  )

  (:action move
    :parameters (?r - robot ?a - place ?b - place)
    :precondition (and (connected ?a ?b) (at-robot ?r ?a) (open ?b))
    :effect (and (at-robot ?r ?b) (not (at-robot ?r ?a)))
  )

  (:action pick-up
    :parameters (?r - robot ?k - key ?p - place)
    :precondition (and (at-robot ?r ?p) (at-key ?k ?p) (arm-empty ?r))
    :effect (and (holding ?r ?k) (not (at-key ?k ?p)) (not (arm-empty ?r)))
  )

  (:action pick-up-drop
    :parameters (?r - robot ?k1 - key ?k2 - key ?p - place)
    :precondition (and (at-robot ?r ?p) (holding ?r ?k2) (at-key ?k1 ?p))
    :effect (and (holding ?r ?k1) (at-key ?k2 ?p) (not (holding ?r ?k2)) (not (at-key ?k1 ?p)))
  )

  (:action put-down
    :parameters (?r - robot ?k - key ?p - place)
    :precondition (and (at-robot ?r ?p) (holding ?r ?k))
    :effect (and (arm-empty ?r) (at-key ?k ?p) (not (holding ?r ?k)))
  )

)