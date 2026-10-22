(define (domain barman)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand - object
    cocktail ingredient - beverage
    glass shaker - container
  )

  (:predicates
    (ontable ?c - container)
    (holding ?h - hand ?c - container)
    (handempty ?h - hand)
    (contains ?c - container ?b - beverage)
    (clean ?c - container)
    (used ?c - container)
    (empty ?c - container)
    (dispenses ?d - dispenser ?i - ingredient)
    (cocktail_part1 ?c - cocktail ?i - ingredient)
    (cocktail_part2 ?c - cocktail ?i - ingredient)
    (shaked ?s - shaker)
    (contains1 ?s - shaker ?i - ingredient)
    (contains2 ?s - shaker ?i - ingredient)
  )

  (:action grasp
    :parameters (?h - hand ?c - container)
    :precondition (and (ontable ?c) (handempty ?h))
    :effect (and (holding ?h ?c) (not (ontable ?c)) (not (handempty ?h)))
  )

  (:action leave
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (ontable ?c) (handempty ?h) (not (holding ?h ?c)))
  )

  (:action fill_shot
    :parameters (?g - glass ?i - ingredient ?h1 - hand ?h2 - hand ?d - dispenser)
    :precondition (and (holding ?h1 ?g) (handempty ?h2) (dispenses ?d ?i) (empty ?g) (clean ?g))
    :effect (and (contains ?g ?i) (not (empty ?g)) (not (clean ?g)) (used ?g))
  )

  (:action pour_shot1_to_shaker
    :parameters (?g - glass ?i - ingredient ?s - shaker ?h - hand)
    :precondition (and (holding ?h ?g) (contains ?g ?i) (empty ?s))
    :effect (and (contains1 ?s ?i) (not (contains ?g ?i)) (empty ?g) (not (empty ?s)))
  )

  (:action pour_shot2_to_shaker
    :parameters (?g - glass ?i - ingredient ?s - shaker ?h - hand)
    :precondition (and (holding ?h ?g) (contains ?g ?i) (not (empty ?s)) (not (shaked ?s)))
    :effect (and (contains2 ?s ?i) (not (contains ?g ?i)) (empty ?g))
  )

  (:action shake
    :parameters (?c - cocktail ?i1 - ingredient ?i2 - ingredient ?s - shaker ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (handempty ?h2) (contains1 ?s ?i1) (contains2 ?s ?i2) (cocktail_part1 ?c ?i1) (cocktail_part2 ?c ?i2))
    :effect (and (shaked ?s) (contains ?s ?c) (not (contains1 ?s ?i1)) (not (contains2 ?s ?i2)))
  )

  (:action pour_shaker_to_glass
    :parameters (?s - shaker ?c - cocktail ?g - glass ?h - hand)
    :precondition (and (holding ?h ?s) (contains ?s ?c) (empty ?g) (clean ?g) (shaked ?s))
    :effect (and (contains ?g ?c) (not (contains ?s ?c)) (empty ?s) (not (shaked ?s)) (not (empty ?g)) (not (clean ?g)) (used ?g))
  )

  (:action clean_glass
    :parameters (?g - glass ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?g) (handempty ?h2) (empty ?g) (used ?g))
    :effect (and (clean ?g) (not (used ?g)))
  )

  (:action clean_shaker
    :parameters (?s - shaker ?h1 - hand ?h2 - hand)
    :precondition (and (holding ?h1 ?s) (handempty ?h2) (empty ?s))
    :effect (clean ?s)
  )

)