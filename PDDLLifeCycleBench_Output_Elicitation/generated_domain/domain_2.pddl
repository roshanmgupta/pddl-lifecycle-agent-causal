(define (domain barman11-bfs)
  (:requirements :strips :typing)
  (:types 
    hand container shot shaker ingredient cocktail dispenser level - object
  )
  (:predicates 
    (on-table ?c - container)
    (holding ?h - hand ?c - container)
    (clean ?c - container)
    (empty ?c - container)
    (contains ?c - container ?b - beverage)
    (dispenses ?d - dispenser ?i - ingredient)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at-level ?s - shaker ?l - level)
    (next-to ?l1 - level ?l2 - level)
  )
  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (on-table ?c) (empty ?h))
    :effect (and (holding ?h ?c) (not (on-table ?c)) (not (empty ?h)))
  )
  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (on-table ?c) (empty ?h) (not (holding ?h ?c)))
  )
  (:action fill
    :parameters (?hC - hand ?hD - hand ?s - shot ?d - dispenser ?i - ingredient)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?i) (not (empty ?s)) (not (clean ?s)))
  )
  (:action refill
    :parameters (?hC - hand ?hD - hand ?s - shot ?d - dispenser ?i - ingredient)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?i) (empty ?s) (used ?s ?i))
    :effect (and (contains ?s ?i) (not (empty ?s)))
  )
  (:action empty-shot
    :parameters (?h - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )
  (:action clean-shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?hC ?s) (empty ?hD) (empty ?s) (used ?s ?b))
    :effect (and (clean ?s) (not (used ?s ?b)))
  )
  (:action pour-to-clean-shaker
    :parameters (?hD - hand ?s - shot ?c - shaker ?i - ingredient ?lE - level ?lF - level)
    :precondition (and (holding ?hD ?s) (contains ?s ?i) (empty ?c) (clean ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (empty ?s) (contains ?c ?i) (unshaken ?c) (at-level ?c ?lF))
  )
  (:action pour-to-used-shaker
    :parameters (?hD - hand ?s - shot ?c - shaker ?i - ingredient ?lE - level ?lF - level)
    :precondition (and (holding ?hD ?s) (contains ?s ?i) (unshaken ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (empty ?s) (contains ?c ?i) (at-level ?c ?lF))
  )
  (:action empty-shaker
    :parameters (?h - hand ?c - shaker ?b - cocktail ?lD - level ?lE - level)
    :precondition (and (holding ?h ?c) (contains ?c ?b) (shaken ?c) (at-level ?c ?lD) (at-level ?c ?lE))
    :effect (and (at-level ?c ?lE) (empty ?c) (not (contains ?c ?b)))
  )
  (:action clean-shaker
    :parameters (?hA - hand ?c - shaker ?hB - hand)
    :precondition (and (holding ?hA ?c) (empty ?hB) (empty ?c))
    :effect (clean ?c)
  )
  (:action shake
    :parameters (?hE - hand ?c - shaker ?hF - hand ?b - ingredient ?c2 - ingredient)
    :precondition (and (holding ?hE ?c) (empty ?hF) (unshaken ?c) (contains ?c ?b) (contains ?c ?c2))
    :effect (and (shaken ?c) (not (unshaken ?c)))
  )
  (:action pour-beverage
    :parameters (?hC - hand ?c - shaker ?s - shot ?b - beverage ?lE - level ?lF - level)
    :precondition (and (holding ?hC ?c) (shaken ?c) (empty ?s) (clean ?s) (contains ?c ?b) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (contains ?s ?b) (at-level ?c ?lF) (not (empty ?s)) (not (clean ?s)))
  )
)