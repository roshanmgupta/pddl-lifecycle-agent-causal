(define (domain goldminer)
  (:requirements :strips :typing)

  (:types
    item loc robot - object
  )

  (:predicates
    (robot-at ?r - robot ?l - loc)
    (connected ?from - loc ?to - loc)
    (clear ?l - loc)
    (holding-laser ?r - robot)
    (holding-bomb ?r - robot)
    (holding-gold ?r - robot)
    (arm-empty ?r - robot)
    (laser-at ?l - loc)
    (bomb-at ?l - loc)
    (gold-at ?l - loc)
    (soft-rock-at ?l - loc)
    (hard-rock-at ?l - loc)
  )

  (:action move
    :parameters (?r - robot ?from - loc ?to - loc)
    :precondition (and (robot-at ?r ?from) (connected ?from ?to) (clear ?to))
    :effect (and (not (robot-at ?r ?from)) (robot-at ?r ?to))
  )

  (:action pick-laser
    :parameters (?r - robot ?l - loc)
    :precondition (and (robot-at ?r ?l) (laser-at ?l) (arm-empty ?r))
    :effect (and (not (laser-at ?l)) (not (arm-empty ?r)) (holding-laser ?r))
  )

  (:action pick-bomb
    :parameters (?r - robot ?l - loc)
    :precondition (and (robot-at ?r ?l) (bomb-at ?l) (arm-empty ?r))
    :effect (and (not (bomb-at ?l)) (not (arm-empty ?r)) (holding-bomb ?r))
  )

  (:action put-laser
    :parameters (?r - robot ?l - loc)
    :precondition (and (robot-at ?r ?l) (holding-laser ?r))
    :effect (and (not (holding-laser ?r)) (arm-empty ?r) (laser-at ?l))
  )

  (:action detonate-bomb
    :parameters (?r - robot ?a - loc ?b - loc)
    :precondition (and (robot-at ?r ?a) (holding-bomb ?r) (connected ?a ?b) (soft-rock-at ?b))
    :effect (and (not (holding-bomb ?r)) (arm-empty ?r) (clear ?b) (not (soft-rock-at ?b)))
  )

  (:action fire-laser
    :parameters (?r - robot ?a - loc ?b - loc)
    :precondition (and (robot-at ?r ?a) (holding-laser ?r) (connected ?a ?b))
    :effect (and (clear ?b) (not (soft-rock-at ?b)) (not (gold-at ?b)) (not (hard-rock-at ?b)))
  )

  (:action pick-gold
    :parameters (?r - robot ?l - loc)
    :precondition (and (robot-at ?r ?l) (arm-empty ?r) (gold-at ?l))
    :effect (and (not (arm-empty ?r)) (holding-gold ?r) (not (gold-at ?l)))
  )

)