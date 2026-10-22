(define (domain barman11-bfs)
  (:requirements :strips :typing)
  (:types
    object
    hand - object
    level - object
    beverage - object
    dispenser - object
    container - object
    ingredient - beverage
    cocktail - beverage
    shot - container
    shaker - container
  )
  (:predicates
    (on-table ?x - container)
    (holding ?h - hand ?c - container)
    (empty ?h - hand)
    (dispenses ?d - dispenser ?i - ingredient)
    (clean ?c - container)
    (used ?c - container ?b - beverage)
    (contains ?c - container ?b - beverage)
    (empty ?c - container)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at-level ?s - shaker ?l - level)
    (next ?l1 - level ?l2 - level)
    (part-of ?c - cocktail ?i - ingredient)
    (another-part-of ?c - cocktail ?i - ingredient)
  )
  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (on-table ?c) (empty ?h))
    :effect (and (holding ?h ?c) (not (on-table ?c)) (not (empty ?h)))
  )
  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (empty ?h) (on-table ?c) (not (holding ?h ?c)))
  )
  (:action fill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?i) (used ?s ?i) (not (empty ?s)) (not (clean ?s)))
  )
  (:action refill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (dispenses ?d ?i) (empty ?s) (used ?s ?i))
    :effect (and (contains ?s ?i) (not (empty ?s)))
  )
  (:action empty-shot
    :parameters (?h - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )
  (:action clean-shot
    :parameters (?s - shot ?b - beverage ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (empty ?s) (used ?s ?b))
    :effect (and (clean ?s) (not (used ?s ?b)))
  )
  (:action pour-clean-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (empty ?sh) (clean ?sh) (at-level ?sh ?l1) (next ?l1 ?l2))
    :effect (and (empty ?s) (contains ?sh ?i) (unshaken ?sh) (at-level ?sh ?l2) (not (contains ?s ?i)) (not (empty ?sh)) (not (clean ?sh)) (not (at-level ?sh ?l1)))
  )
  (:action pour-used-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (unshaken ?sh) (at-level ?sh ?l1) (next ?l1 ?l2))
    :effect (and (contains ?sh ?i) (empty ?s) (at-level ?sh ?l2) (not (contains ?s ?i)) (not (at-level ?sh ?l1)))
  )
  (:action empty-shaker
    :parameters (?h - hand ?sh - shaker ?c - cocktail ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (contains ?sh ?c) (shaken ?sh) (at-level ?sh ?l1) (at-level ?sh ?l2))
    :effect (and (at-level ?sh ?l2) (empty ?sh) (not (shaken ?sh)) (not (at-level ?sh ?l1)) (not (contains ?sh ?c)))
  )
  (:action clean-shaker
    :parameters (?sh - shaker ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?sh) (empty ?h2) (empty ?sh))
    :effect (clean ?sh)
  )
  (:action shake
    :parameters (?c - cocktail ?sh - shaker ?h1 - hand ?h2 - hand ?i1 - ingredient ?i2 - ingredient)
    :precondition (and (holding ?h1 ?sh) (empty ?h2) (contains ?sh ?i1) (contains ?sh ?i2) (part-of ?c ?i1) (another-part-of ?c ?i2) (unshaken ?sh))
    :effect (and (shaken ?sh) (contains ?sh ?c) (not (unshaken ?sh)) (not (contains ?sh ?i1)) (not (contains ?sh ?i2)))
  )
  (:action pour-shaker-to-shot
    :parameters (?b - beverage ?sh - shaker ?h - hand ?s - shot ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (shaken ?sh) (empty ?s) (clean ?s) (contains ?sh ?b) (at-level ?sh ?l1) (next ?l1 ?l2))
    :effect (and (contains ?s ?b) (at-level ?sh ?l2) (not (clean ?s)) (not (empty ?s)) (not (at-level ?sh ?l1)))
  )
)