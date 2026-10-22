(define (domain freecell)
  (:requirements :strips :typing)

  (:types
    card container - object
    foundation freecell pile - container
  )

  (:predicates
    (on ?c1 - card ?c2 - card)
    (top ?c - card ?p - pile)
    (in_freecell ?c - card ?f - freecell)
    (in_foundation ?c - card ?f - foundation)
    (empty_freecell ?f - freecell)
    (empty_pile ?p - pile)
    (empty_foundation ?f - foundation)
  )

  (:action move_card_to_freecell
    :parameters (?c - card ?p - pile ?f - freecell)
    :precondition (and (top ?c ?p) (empty_freecell ?f))
    :effect (and (not (top ?c ?p)) (in_freecell ?c ?f) (empty_pile ?p))
  )

  (:action move_card_to_foundation
    :parameters (?c - card ?p - pile ?f - foundation)
    :precondition (and (top ?c ?p) (empty_foundation ?f))
    :effect (and (not (top ?c ?p)) (in_foundation ?c ?f) (empty_pile ?p))
  )

  (:action move_card_between_piles
    :parameters (?c1 - card ?p1 - pile ?c2 - card ?p2 - pile)
    :precondition (and (top ?c1 ?p1) (top ?c2 ?p2))
    :effect (and (not (top ?c1 ?p1)) (not (top ?c2 ?p2)) (on ?c1 ?c2) (top ?c1 ?p2))
  )

)