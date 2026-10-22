(define (domain barman14-bfs)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand level object - object
    cocktail ingredient - beverage
    shaker shot - container
  )

  (:predicates
    (on-table ?b - container)
    (holding ?h - hand ?c - container)
    (hand-empty ?h - hand)
    (dispenses ?d - dispenser ?i - ingredient)
    (clean ?c - container)
    (empty ?c - container)
    (contains ?c - container ?b - beverage)
    (used-by ?c - container ?b - beverage)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at-level ?s - shaker ?l - level)
    (at-empty-level ?s - shaker ?l - level)
    (next-to ?l1 - level ?l2 - level)
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

  (:action pour-clean-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (empty ?c) (clean ?c) (at-level ?c ?e) (next-to ?e ?f))
    :effect (and (empty ?a) (contains ?c ?b) (unshaken ?c) (at-level ?c ?f) (not (contains ?a ?b)) (not (empty ?c)) (not (clean ?c)) (not (at-level ?c ?e)))
  )

  (:action pour-used-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (unshaken ?c) (at-level ?c ?e) (next-to ?e ?f))
    :effect (and (contains ?c ?b) (empty ?a) (at-level ?c ?f) (not (contains ?a ?b)) (not (at-level ?c ?e)))
  )

  (:action empty-shaker
    :parameters (?a - hand ?b - shaker ?c - cocktail ?d - level ?e - level)
    :precondition (and (holding ?a ?b) (contains ?b ?c) (shaken ?b) (at-level ?b ?d) (at-empty-level ?b ?e))
    :effect (and (at-level ?b ?e) (empty ?b) (not (shaken ?b)) (not (at-level ?b ?d)) (not (contains ?b ?c)))
  )

  (:action clean-shaker
    :parameters (?a - hand ?b - hand ?c - shaker)
    :precondition (and (holding ?a ?c) (hand-empty ?b) (empty ?c))
    :effect (clean ?c)
  )

  (:action shake
    :parameters (?a - cocktail ?b - ingredient ?c - ingredient ?d - shaker ?e - hand ?f - hand)
    :precondition (and (holding ?e ?d) (hand-empty ?f) (contains ?d ?b) (part-of ?a ?b) (unshaken ?d))
    :effect (and (shaken ?d) (contains ?d ?a) (not (unshaken ?d)) (not (contains ?d ?b)))
  )

  (:action pour-beverage
    :parameters (?a - beverage ?b - shot ?c - hand ?d - shaker ?e - level ?f - level)
    :precondition (and (holding ?c ?d) (shaken ?d) (empty ?b) (clean ?b) (contains ?d ?a) (at-level ?d ?e) (next-to ?e ?f))
    :effect (and (contains ?b ?a) (at-level ?d ?f) (not (clean ?b)) (not (empty ?b)) (not (at-level ?d ?e)))
  )

)