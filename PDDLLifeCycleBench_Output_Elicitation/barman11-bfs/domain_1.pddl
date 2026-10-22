(define (domain barman11-bfs)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand level - object
    cocktail ingredient - beverage
    shaker shot - container
  )

  (:predicates
    (on-table ?b - container)
    (holding ?h - hand ?b - container)
    (empty ?h - hand)
    (clean ?b - container)
    (contains ?s - shot ?c - cocktail)
    (contains-cocktail ?s - shot ?c - cocktail)
    (dispenses ?d - dispenser ?i - ingredient)
    (next-to ?l1 - level ?l2 - level)
    (shaken ?s - shaker)
    (empty-shot ?s - shot)
  )

  (:action grasp-container
    :parameters (?a - hand ?b - container)
    :precondition (and (on-table ?b) (empty ?a))
    :effect (and (holding ?a ?b) (not (on-table ?b)) (not (empty ?a)))
  )

  (:action leave-container
    :parameters (?a - hand ?b - container)
    :precondition (holding ?a ?b)
    :effect (and (empty ?a) (on-table ?b) (not (holding ?a ?b)))
  )

  (:action fill-shot
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (dispenses ?e ?b) (empty-shot ?a) (clean ?a))
    :effect (and (contains-cocktail ?a ?b) (not (empty ?a)) (not (clean ?a)))
  )

  (:action refill-shot
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (dispenses ?e ?b) (empty ?a) (used ?a ?b))
    :effect (and (contains-cocktail ?a ?b) (not (empty ?a)))
  )

  (:action empty-shot
    :parameters (?a - hand ?b - shot ?c - beverage)
    :precondition (and (holding ?a ?b) (contains ?b ?c))
    :effect (and (empty ?b) (not (contains ?b ?c)))
  )

  (:action clean-shot
    :parameters (?a - shot ?b - beverage ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (used ?a ?b) (not (empty ?a)))
    :effect (and (clean ?a) (not (used ?a ?b)))
  )

  (:action pour-into-clean-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (empty ?c) (clean ?c) (at-level ?c ?e) (next-to ?e ?f))
    :effect (and (empty ?a) (contains ?c ?b) (not (empty ?c)) (not (clean ?c)) (at-level ?c ?f))
  )

  (:action pour-into-used-shaker
    :parameters (?a - shot ?b - ingredient ?c - shaker ?d - hand ?e - level ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (not (clean ?c)) (at-level ?c ?e) (next-to ?e ?f))
    :effect (and (contains ?c ?b) (empty ?a) (at-level ?c ?f))
  )

  (:action empty-shaker
    :parameters (?a - hand ?b - shaker ?c - cocktail ?d - level ?e - level)
    :precondition (and (holding ?a ?b) (contains ?b ?c) (shaken ?b) (at-level ?b ?d) (at-empty-level ?b ?e))
    :effect (and (at-level ?b ?e) (empty ?b) (not (contains ?b ?c)) (not (shaken ?b)) (not (at-level ?b ?d)))
  )

  (:action clean-shaker
    :parameters (?a - shaker ?b - hand)
    :precondition (and (holding ?a ?b) (empty ?b) (empty ?a))
    :effect (clean ?a)
  )

  (:action shake-cocktail
    :parameters (?a - cocktail ?b - shaker ?c - hand ?d - hand ?e - ingredient ?f - ingredient)
    :precondition (and (holding ?c ?b) (empty ?d) (contains ?b ?e) (contains ?b ?f) (part-of ?e ?a) (part-of ?f ?a) (not (shaken ?b)))
    :effect (and (shaken ?b) (contains ?b ?a) (not (not (shaken ?b))) (not (contains ?b ?e)) (not (contains ?b ?f)))
  )

  (:action pour-beverage
    :parameters (?a - beverage ?b - shaker ?c - hand ?d - shot ?e - level ?f - level)
    :precondition (and (holding ?c ?b) (shaken ?b) (empty ?d) (clean ?d) (contains ?b ?a) (at-level ?b ?e) (next-to ?e ?f))
    :effect (and (contains ?d ?a) (at-level ?b ?f) (not (clean ?d)) (not (empty ?d)) (not (at-level ?b ?e)))
  )

)