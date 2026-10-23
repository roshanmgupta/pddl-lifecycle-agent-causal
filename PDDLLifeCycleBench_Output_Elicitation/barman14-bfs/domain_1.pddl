(define (domain barman14-bfs)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand level - object
    shaker shot - container
    cocktail ingredient - beverage
  )

  (:predicates
    (on-table ?c - container)
    (holding ?h - hand ?c - container)
    (empty ?h - object)
    (clean ?c - container)
    (contains ?c - container ?b - beverage)
    (dispenses ?d - dispenser ?i - ingredient)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at-level ?s - shaker ?l - level)
    (next-to ?l1 - level ?l2 - level)
    (part-of ?c - object ?i - beverage)
  )

  (:action grasp_container
    :parameters (?h - hand ?c - container)
    :precondition (and (on-table ?c) (empty ?h))
    :effect (and (holding ?h ?c) (not (on-table ?c)) (not (empty ?h)))
  )

  (:action leave_container
    :parameters (?h - hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (empty ?h) (on-table ?c) (not (holding ?h ?c)))
  )

  (:action fill_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?i - ingredient ?d - dispenser)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?i) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?i) (not (empty ?s)) (not (clean ?s)))
  )

  (:action refill_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?i - ingredient ?d - dispenser)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?i) (empty ?s) (not (clean ?s)) (part-of ?s ?i))
    :effect (and (contains ?s ?i) (not (empty ?s)))
  )

  (:action empty_shot
    :parameters (?h - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )

  (:action clean_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?hC ?s) (empty ?hD) (not (empty ?s)) (part-of ?s ?b))
    :effect (and (clean ?s) (not (part-of ?s ?b)))
  )

  (:action pour_into_clean_shaker
    :parameters (?h - hand ?s - shot ?i - ingredient ?c - shaker ?lE - level ?lF - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (empty ?c) (clean ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (empty ?s) (contains ?c ?i) (unshaken ?c) (at-level ?c ?lF))
  )

  (:action pour_into_used_shaker
    :parameters (?h - hand ?s - shot ?i - ingredient ?c - shaker ?lE - level ?lF - level)
    :precondition (and (holding ?h ?s) (contains ?s ?i) (not (empty ?c)) (shaken ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (contains ?c ?i) (empty ?s) (at-level ?c ?lF))
  )

  (:action empty_shaker
    :parameters (?h - hand ?c - shaker ?b - cocktail ?lD - level ?lE - level)
    :precondition (and (holding ?h ?c) (contains ?c ?b) (shaken ?c) (at-level ?c ?lD) (next-to ?lD ?lE))
    :effect (and (at-level ?c ?lE) (empty ?c) (not (contains ?c ?b)))
  )

  (:action clean_shaker
    :parameters (?h - hand ?c - shaker)
    :precondition (and (holding ?h ?c) (empty ?h) (empty ?c))
    :effect (clean ?c)
  )

  (:action shake_cocktail
    :parameters (?hE - hand ?hF - hand ?c - shaker ?b - ingredient ?i - ingredient ?cocktail - cocktail)
    :precondition (and (holding ?hE ?c) (empty ?hF) (contains ?c ?b) (contains ?c ?i) (part-of ?cocktail ?b) (part-of ?cocktail ?i) (unshaken ?c))
    :effect (and (shaken ?c) (contains ?c ?cocktail))
  )

  (:action pour_beverage
    :parameters (?h - hand ?c - shaker ?b - beverage ?s - shot ?lE - level ?lF - level)
    :precondition (and (holding ?h ?c) (shaken ?c) (empty ?s) (clean ?s) (contains ?c ?b) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (contains ?s ?b) (at-level ?c ?lF) (not (empty ?s)) (not (empty ?c)))
  )

)