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
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (part-of ?c - cocktail ?i - ingredient)
    (another-part-of ?c - cocktail ?i - ingredient)
  )

  (:action grasp
    :parameters (?a - hand ?b - container)
    :precondition (and (on-table ?b) (hand-empty ?a))
    :effect (and (holding ?a ?b) (not (on-table ?b)) (not (hand-empty ?a)))
  )

  (:action leave
    :parameters (?a - hand ?b - container)
    :precondition (holding ?a ?b)
    :effect (and (hand-empty ?a) (on-table ?b) (not (holding ?a ?b)))
  )

  (:action fill
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (hand-empty ?d) (dispenses ?e ?b) (empty ?a) (clean ?a))
    :effect (and (contains ?a ?b) (used-by ?a ?b) (not (empty ?a)) (not (clean ?a)))
  )

  (:action refill
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (hand-empty ?d) (dispenses ?e ?b) (empty ?a) (used-by ?a ?b))
    :effect (and (contains ?a ?b) (not (empty ?a)))
  )

  (:action empty-shot
    :parameters (?a - hand ?b - shot ?c - beverage)
    :precondition (and (holding ?a ?b) (contains ?b ?c))
    :effect (and (empty ?b) (not (contains ?b ?c)))
  )

  (:action clean-shot
    :parameters (?a - shot ?b - beverage ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (hand-empty ?d) (empty ?a) (used-by ?a ?b))
    :effect (and (clean ?a) (not (used-by ?a ?b)))
  )

  (:action pour-into-clean-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (empty ?c) (clean ?c) (shaker-at-level ?c ?e) (next-to ?e ?f))
    :effect (and (empty ?a) (contains ?c ?b) (unshaken ?c) (shaker-at-level ?c ?f) (not (contains ?a ?b)) (not (empty ?c)) (not (clean ?c)) (not (shaker-at-level ?c ?e)))
  )

  (:action pour-into-used-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (unshaken ?c) (shaker-at-level ?c ?e) (next-to ?e ?f))
    :effect (and (contains ?c ?b) (empty ?a) (shaker-at-level ?c ?f) (not (contains ?a ?b)) (not (shaker-at-level ?c ?e)))
  )

  (:action empty-shaker
    :parameters (?a - hand ?b - shaker ?c - cocktail ?d - level ?e - level)
    :precondition (and (holding ?a ?b) (contains ?b ?c) (shaken ?b) (shaker-at-level ?b ?d) (shaker-at-empty-level ?b ?e))
    :effect (and (shaker-at-level ?b ?e) (empty ?b) (not (shaken ?b)) (not (shaker-at-level ?b ?d)) (not (contains ?b ?c)))
  )

  (:action clean-shaker
    :parameters (?a - hand ?b - hand ?c - shaker)
    :precondition (and (holding ?a ?c) (hand-empty ?b) (empty ?c))
    :effect (clean ?c)
  )

  (:action shake
    :parameters (?a - cocktail ?b - ingredient ?c - ingredient ?d - shaker ?e - hand ?f - hand)
    :precondition (and (holding ?e ?d) (hand-empty ?f) (or (contains ?d ?b) (contains ?d ?c)) (part-of ?a ?b) (another-part-of ?a ?c) (unshaken ?d))
    :effect (and (shaken ?d) (contains ?d ?a) (not (unshaken ?d)) (not (contains ?d ?b)) (not (contains ?d ?c)))
  )

  (:action pour-from-shaker
    :parameters (?a - beverage ?b - shot ?c - hand ?d - shaker ?e - level ?f - level)
    :precondition (and (holding ?c ?d) (shaken ?d) (empty ?b) (clean ?b) (contains ?d ?a) (or (shaker-at-level ?d ?e) (shaker-at-empty-level ?d ?e)) (next-to ?e ?f))
    :effect (and (contains ?b ?a) (shaker-at-level ?d ?f) (not (clean ?b)) (not (empty ?b)) (not (shaker-at-level ?d ?e)) (not (shaker-at-empty-level ?d ?e)))
  )

)