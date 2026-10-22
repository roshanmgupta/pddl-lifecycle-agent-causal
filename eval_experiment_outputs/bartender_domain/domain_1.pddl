(define (domain bartender_domain)
  (:requirements :strips :typing)

  (:types
    container dispenser ingredient robot_hand sink - object
    cocktail_glass shaker - container
  )

  (:predicates
    (holding ?h - robot_hand ?c - container)
    (clean ?c - container)
    (dirty ?c - container)
    (contains ?c - container ?i - ingredient)
    (empty ?c - container)
    (at_dispenser ?d - dispenser ?i - ingredient)
    (at_sink ?s - sink)
    (mixed ?c - container)
    (empty_hand ?h - robot_hand)
  )

  (:action grasp
    :parameters (?h - robot_hand ?c - container)
    :precondition (and (empty ?c) (clean ?c) (empty_hand ?h))
    :effect (and (holding ?h ?c) (not (empty ?c)) (not (clean ?c)) (not (empty_hand ?h)))
  )

  (:action pour_ingredient
    :parameters (?h - robot_hand ?c - container ?d - dispenser ?i - ingredient)
    :precondition (and (holding ?h ?c) (at_dispenser ?d ?i))
    :effect (and (contains ?c ?i) (not (empty ?c)))
  )

  (:action pour_into_shaker
    :parameters (?h1 - robot_hand ?h2 - robot_hand ?sg - container ?sh - shaker ?i - ingredient)
    :precondition (and (holding ?h1 ?sg) (contains ?sg ?i) (clean ?sh) (empty ?sh) (holding ?h2 ?sh) (empty_hand ?h2))
    :effect (and (contains ?sh ?i) (empty ?sg) (dirty ?sg) (not (empty ?sh)))
  )

  (:action shake
    :parameters (?h - robot_hand ?sh - shaker ?i - ingredient)
    :precondition (and (holding ?h ?sh) (contains ?sh ?i))
    :effect (mixed ?sh)
  )

  (:action pour_cocktail
    :parameters (?h - robot_hand ?sh - shaker ?cg - cocktail_glass ?i - ingredient)
    :precondition (and (holding ?h ?sh) (mixed ?sh) (empty ?cg))
    :effect (and (contains ?cg ?i) (empty ?sh) (dirty ?sh) (not (empty ?cg)))
  )

  (:action clean_container
    :parameters (?h - robot_hand ?c - container ?s - sink)
    :precondition (and (holding ?h ?c) (dirty ?c) (at_sink ?s))
    :effect (and (clean ?c) (not (dirty ?c)))
  )

  (:action release
    :parameters (?h - robot_hand ?c - container)
    :precondition (holding ?h ?c)
    :effect (and (empty_hand ?h) (not (holding ?h ?c)))
  )

)