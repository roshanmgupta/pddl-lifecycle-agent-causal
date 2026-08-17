(define (domain warehouse_logistics)
  (:requirements :strips :typing)

  (:types
    robot crate location - object
  )

  (:predicates
    (at?r - robot?l - location)
    (at?c - crate?l - location)
    (connected?l1 - location?l2 - location)
    (hand-empty?r - robot)
    (holding?r - robot?c - crate)
  )

  (:action move_robot
    :parameters (?r - robot ?from - location ?to - location)
    :precondition (and (at?r?from) (connected?from?to))
    :effect (and (at?r?to) (not (at?r?from)))
  )

  (:action pick_up_crate
    :parameters (?r - robot ?c - crate ?l - location)
    :precondition (and (at?r?l) (at?c?l) (hand-empty?r))
    :effect (and (holding?r?c) (not (at?c?l)) (not (hand-empty?r)))
  )

  (:action drop_crate
    :parameters (?r - robot ?c - crate ?l - location)
    :precondition (and (at?r?l) (holding?r?c))
    :effect (and (at?c?l) (hand-empty?r) (not (holding?r?c)))
  )

)