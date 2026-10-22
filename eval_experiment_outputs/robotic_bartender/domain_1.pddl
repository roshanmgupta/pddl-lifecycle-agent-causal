(define (domain robotic_bartender)
  (:requirements :strips :typing)

  (:types
    cocktail_glass dispenser hand ingredient shaker shot_glass sink - object
  )

  (:predicates
    (hand_empty ?h - hand)
    (holding ?h - hand ?s - shot_glass)
    (clean_shot ?s - shot_glass)
    (clean_shaker ?sh - shaker)
    (clean_glass ?cg - cocktail_glass)
    (dirty_shot ?s - shot_glass)
    (dirty_shaker ?sh - shaker)
    (empty_shot ?s - shot_glass)
    (contains_shot ?s - shot_glass ?i - ingredient)
    (contains_shaker ?sh - shaker ?i - ingredient)
    (mixed ?sh - shaker)
    (ready ?cg - cocktail_glass)
    (dispenser_clean ?d - dispenser)
    (dispenser_has ?d - dispenser ?i - ingredient)
    (recipe ?sh - shaker ?i - ingredient)
    (at ?h - hand ?s - sink)
  )

  (:action grasp_shot
    :parameters (?h - hand ?s - shot_glass)
    :precondition (and (hand_empty ?h) (clean_shot ?s) (empty_shot ?s))
    :effect (and (not (hand_empty ?h)) (holding ?h ?s))
  )

  (:action dispense_ingredient
    :parameters (?h - hand ?s - shot_glass ?d - dispenser ?i - ingredient)
    :precondition (and (holding ?h ?s) (empty_shot ?s) (dispenser_clean ?d) (dispenser_has ?d ?i))
    :effect (and (not (empty_shot ?s)) (contains_shot ?s ?i))
  )

  (:action pour_shot_to_shaker
    :parameters (?h - hand ?s - shot_glass ?sh - shaker ?i - ingredient)
    :precondition (and (holding ?h ?s) (contains_shot ?s ?i) (clean_shaker ?sh))
    :effect (and (not (contains_shot ?s ?i)) (empty_shot ?s) (dirty_shot ?s) (contains_shaker ?sh ?i) (dirty_shaker ?sh) (not (clean_shaker ?sh)))
  )

  (:action release_shot
    :parameters (?h - hand ?s - shot_glass)
    :precondition (holding ?h ?s)
    :effect (and (hand_empty ?h) (not (holding ?h ?s)))
  )

  (:action wash_shot_glass
    :parameters (?h - hand ?s - shot_glass ?sink - sink)
    :precondition (and (hand_empty ?h) (dirty_shot ?s) (at ?h ?sink))
    :effect (and (clean_shot ?s) (not (dirty_shot ?s)))
  )

  (:action wash_shaker
    :parameters (?h - hand ?sh - shaker ?sink - sink)
    :precondition (and (hand_empty ?h) (dirty_shaker ?sh) (at ?h ?sink))
    :effect (and (clean_shaker ?sh) (not (dirty_shaker ?sh)))
  )

  (:action shake_shaker
    :parameters (?h1 - hand ?h2 - hand ?sh - shaker ?i1 - ingredient ?i2 - ingredient)
    :precondition (and (hand_empty ?h1) (hand_empty ?h2) (recipe ?sh ?i1) (recipe ?sh ?i2) (contains_shaker ?sh ?i1) (contains_shaker ?sh ?i2) (not (mixed ?sh)))
    :effect (mixed ?sh)
  )

  (:action decant_shaker_to_glass
    :parameters (?sh - shaker ?cg - cocktail_glass)
    :precondition (and (mixed ?sh) (clean_glass ?cg))
    :effect (and (ready ?cg) (dirty_shaker ?sh) (not (mixed ?sh)) (not (clean_shaker ?sh)))
  )

)