(define (domain barman14-bfs)
  (:requirements :strips :typing)

  (:types
    beverage container dispenser hand level table - object
    cocktail ingredient - beverage
    shaker shot - container
  )

  (:predicates
    (on ?c - container ?t - object)
    (holding ?h - hand ?c - container)
    (empty ?h - object)
    (clean ?c - container)
    (contains ?c - container ?b - beverage)
    (dispenses ?d - dispenser ?b - ingredient)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at-level ?s - shaker ?l - level)
    (next-to ?l1 - level ?l2 - level)
    (part-of ?c - beverage ?i - beverage)
  )

  (:action grasp_container
    :parameters (?h - hand ?c - container ?t - object)
    :precondition (and (on ?c ?t) (empty ?h))
    :effect (and (holding ?h ?c) (not (on ?c ?t)) (not (empty ?h)))
  )

  (:action leave_container
    :parameters (?h - hand ?c - container ?t - object)
    :precondition (holding ?h ?c)
    :effect (and (empty ?h) (on ?c ?t) (not (holding ?h ?c)))
  )

  (:action fill_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?b - ingredient ?d - dispenser)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?b) (empty ?s) (clean ?s))
    :effect (and (contains ?s ?b) (not (empty ?s)) (not (clean ?s)))
  )

  (:action refill_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?b - ingredient ?d - dispenser)
    :precondition (and (holding ?hC ?s) (empty ?hD) (dispenses ?d ?b) (not (empty ?s)) (not (clean ?s)))
    :effect (and (contains ?s ?b) (not (empty ?s)))
  )

  (:action empty_shot
    :parameters (?h - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?h ?s) (contains ?s ?b))
    :effect (and (empty ?s) (not (contains ?s ?b)))
  )

  (:action clean_shot
    :parameters (?hC - hand ?hD - hand ?s - shot ?b - beverage)
    :precondition (and (holding ?hC ?s) (empty ?hD) (not (empty ?s)) (contains ?s ?b))
    :effect (and (clean ?s) (not (contains ?s ?b)))
  )

  (:action pour_into_clean_shaker
    :parameters (?h - hand ?s - shot ?b - ingredient ?c - shaker ?lE - level ?lF - level)
    :precondition (and (holding ?h ?s) (contains ?s ?b) (empty ?c) (clean ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (empty ?s) (contains ?c ?b) (unshaken ?c) (at-level ?c ?lF))
  )

  (:action pour_into_used_shaker
    :parameters (?h - hand ?s - shot ?b - ingredient ?c - shaker ?lE - level ?lF - level)
    :precondition (and (holding ?h ?s) (contains ?s ?b) (not (empty ?c)) (shaken ?c) (at-level ?c ?lE) (next-to ?lE ?lF))
    :effect (and (contains ?c ?b) (empty ?s) (at-level ?c ?lF))
  )

  (:action empty_shaker
    :parameters (?h - hand ?s - shaker ?c - cocktail ?lD - level ?lE - level)
    :precondition (and (holding ?h ?s) (contains ?s ?c) (shaken ?s) (at-level ?s ?lD) (next-to ?lD ?lE))
    :effect (and (empty ?s) (at-level ?s ?lE) (not (contains ?s ?c)))
  )

  (:action clean_shaker
    :parameters (?h - hand ?s - shaker)
    :precondition (and (holding ?h ?s) (empty ?h) (not (empty ?s)))
    :effect (clean ?s)
  )

  (:action shake_cocktail
    :parameters (?hE - hand ?hF - hand ?c - cocktail ?s - shaker ?b - ingredient ?i - ingredient)
    :precondition (and (holding ?hE ?s) (empty ?hF) (contains ?s ?b) (contains ?s ?i) (part-of ?b ?c) (part-of ?i ?c) (unshaken ?s))
    :effect (and (shaken ?s) (contains ?s ?c))
  )

  (:action pour_beverage
    :parameters (?h - hand ?s - shaker ?b - beverage ?s2 - shot ?lE - level ?lF - level)
    :precondition (and (holding ?h ?s) (shaken ?s) (empty ?s2) (clean ?s2) (contains ?s ?b) (at-level ?s ?lE) (next-to ?lE ?lF))
    :effect (and (contains ?s2 ?b) (at-level ?s ?lF) (not (clean ?s2)) (not (empty ?s2)))
  )

)