(define (domain barman14-bfs)
  (:requirements :strips :typing)
  (:types 
    hand level beverage ingredient cocktail container shot shaker - object
  )
  
  (:predicates 
    (on-table ?c - container)
    (clean ?c - container)
    (empty ?c - container)
    (holding ?h - hand ?c - container)
    (dispenses ?d - dispenser ?i - ingredient)
    (contains ?c - container ?b - beverage)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (next-to ?l1 - level ?l2 - level)
    (part-of ?c - cocktail ?i - ingredient)
  )

  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (on-table ?c) (empty ?h))
    :effect (and (holding ?h ?c) (not (on-table ?c)) (not (empty ?h)))
  )

  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (not (holding ?h ?c)) (on-table ?c) (empty ?h))
  )

  (:action fill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?i) (not (empty ?s)) (not (clean ?s)))
  )

  (:action refill
    :parameters (?s - shot ?i - ingredient ?d - dispenser ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (dispenses ?d ?i) (empty ?s) (not (clean ?s)))
    :effect (and (contains ?s ?i) (not (empty ?s)))
  )

  (:action empty-shot
    :parameters (?s - shot ?b - beverage ?h - hand)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )

  (:action clean-shot
    :parameters (?s - shot ?b - beverage ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (empty ?h2) (empty ?s) (not (clean ?s)))
    :effect (and (clean ?s) (not (used ?s ?b)))
  )

  (:action pour-to-clean-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (empty ?sh) (clean ?sh) (next-to ?l1 ?l2))
    :effect (and (empty ?s) (contains ?sh ?i) (unshaken ?sh) (not (empty ?sh)))
  )

  (:action pour-to-used-shaker
    :parameters (?s - shot ?i - ingredient ?sh - shaker ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (not (clean ?sh)) (next-to ?l1 ?l2))
    :effect (and (empty ?s) (contains ?sh ?i))
  )

  (:action empty-shaker
    :parameters (?sh - shaker ?c - cocktail ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (contains ?sh ?c) (shaken ?sh) (next-to ?l1 ?l2))
    :effect (and (empty ?sh) (not (contains ?sh ?c)))
  )

  (:action clean-shaker
    :parameters (?sh - shaker ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?sh) (empty ?h2) (empty ?sh))
    :effect (clean ?sh)
  )

  (:action shake
    :parameters (?c - cocktail ?sh - shaker ?h1 - hand ?h2 - hand ?i1 - ingredient ?i2 - ingredient)
    :precondition (and (holding ?h1 ?sh) (empty ?h2) (not (shaken ?sh)) (contains ?sh ?i1) (contains ?sh ?i2))
    :effect (and (shaken ?sh) (not (unshaken ?sh)))
  )

  (:action pour-beverage
    :parameters (?b - beverage ?sh - shaker ?s - shot ?h - hand ?l1 - level ?l2 - level)
    :precondition (and (holding ?h ?sh) (shaken ?sh) (empty ?s) (clean ?s) (contains ?sh ?b) (next-to ?l1 ?l2))
    :effect (and (contains ?s ?b) (empty ?sh))
  )
)