(define (domain jump_move_domain)
  (:requirements :strips :typing)

  (:types
    location move - object
    continue-jump jump - move
  )

  (:predicates
    (move-ended)
    (in-line ?a - location ?b - location ?c - location)
    (occupied ?loc - location)
    (free ?loc - location)
    (last-visited ?loc - location)
  )

  (:action jump-new-move
    :parameters (?a - location ?b - location ?c - location)
    :precondition (and (move-ended) (in-line ?a ?b ?c) (occupied ?a) (occupied ?b) (free ?c))
    :effect (and (not (occupied ?a)) (not (occupied ?b)) (occupied ?c) (not (move-ended)) (last-visited ?c) (not (free ?c)))
  )

  (:action continue-jump
    :parameters (?a - location ?b - location ?c - location)
    :precondition (and (last-visited ?a) (in-line ?a ?b ?c) (occupied ?a) (occupied ?b) (free ?c))
    :effect (and (not (occupied ?a)) (not (occupied ?b)) (occupied ?c) (last-visited ?c) (not (free ?c)))
  )

  (:action end-move
    :parameters (?a - location)
    :precondition (last-visited ?a)
    :effect (and (move-ended) (not (last-visited ?a)))
  )

)