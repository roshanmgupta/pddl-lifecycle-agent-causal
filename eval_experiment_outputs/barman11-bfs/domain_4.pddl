(define (domain barman11-bfs)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand level object - object
    cocktail ingredient - beverage
    shaker shot - container
  )

  (:predicates
    (on-table ?c - container)
    (holding ?h - hand ?c - container)
    (hand-empty ?h - hand)
    (dispenses ?d - dispenser ?i - ingredient)
    (clean ?c - container)
    (empty ?c - container)
    (contains ?c - container ?b - beverage)
    (used-by ?c - container ?b - beverage)
    (shaker-at-level ?s - shaker ?l - level)
    (shaker-at-empty-level ?s - shaker ?l - level)
    (next-to ?l1 - level ?l2 - level)
    (part-of ?c - cocktail ?i - ingredient)
    (another-part-of ?c - cocktail ?i - ingredient)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
  )

  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (on-table ?c) (hand-empty ?h))
    :effect (and (holding ?h ?c) (not (on-table ?c)) (not (hand-empty ?h)))
  )

  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (hand-empty ?h) (on-table ?c) (not (holding ?h ?c)))
  )

  (:action fill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h - hand ?e - hand)
    :precondition (and (holding ?h ?s) (hand-empty ?e) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?i) (used-by ?s ?i) (not (empty ?s)) (not (clean ?s)))
  )

  (:action refill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h - hand ?e - hand)
    :precondition (and (holding ?h ?s) (hand-empty ?e) (dispenses ?d ?i) (empty ?s) (used-by ?s ?i))
    :effect (and (contains ?s ?i) (not (empty ?s)))
  )

  (:action empty-shot
    :parameters (?h - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )

  (:action clean-shot
    :parameters (?s - shot ?b - beverage ?h - hand ?e - hand)
    :precondition (and (holding ?h ?s) (hand-empty ?e) (empty ?s) (used-by ?s ?b))
    :effect (and (clean ?s) (not (used-by ?s ?b)))
  )

  (:action pour-clean-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (empty ?sh) (clean ?sh) (shaker-at-level ?sh ?l1) (next-to ?l1 ?l2))
    :effect (and (empty ?s) (contains ?sh ?i) (unshaken ?sh) (shaker-at-level ?sh ?l2) (not (contains ?s ?i)) (not (empty ?sh)) (not (clean ?sh)) (not (shaker-at-level ?sh ?l1)))
  )

  (:action pour-used-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (unshaken ?sh) (shaker-at-level ?sh ?l1) (next-to ?l1 ?l2))
    :effect (and (contains ?sh ?i) (empty ?s) (shaker-at-level ?sh ?l2) (not (contains ?s ?i)) (not (shaker-at-level ?sh ?l1)))
  )

  (:action empty-shaker
    :parameters (?h - hand ?sh - shaker ?c - cocktail ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (contains ?sh ?c) (shaken ?sh) (shaker-at-level ?sh ?l1) (shaker-at-empty-level ?sh ?l2))
    :effect (and (shaker-at-level ?sh ?l2) (empty ?sh) (not (shaken ?sh)) (not (shaker-at-level ?sh ?l1)) (not (contains ?sh ?c)))
  )

  (:action clean-shaker
    :parameters (?h - hand ?sh - shaker ?e - hand)
    :precondition (and (holding ?h ?sh) (hand-empty ?e) (empty ?sh))
    :effect (clean ?sh)
  )

  (:action shake
    :parameters (?c - cocktail ?sh - shaker ?h - hand ?e - hand ?i1 - ingredient ?i2 - ingredient)
    :precondition (and (holding ?h ?sh) (hand-empty ?e) (or (contains ?sh ?i1) (contains ?sh ?i2)) (part-of ?c ?i1) (another-part-of ?c ?i2) (unshaken ?sh))
    :effect (and (shaken ?sh) (contains ?sh ?c) (not (unshaken ?sh)) (not (contains ?sh ?i1)) (not (contains ?sh ?i2)))
  )

  (:action pour-beverage
    :parameters (?b - beverage ?sh - shaker ?h - hand ?s - shot ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (shaken ?sh) (contains ?sh ?b) (shaker-at-level ?sh ?l1) (next-to ?l1 ?l2))
    :effect (and (contains ?s ?b) (shaker-at-level ?sh ?l2) (not (shaker-at-level ?sh ?l1)))
  )

)