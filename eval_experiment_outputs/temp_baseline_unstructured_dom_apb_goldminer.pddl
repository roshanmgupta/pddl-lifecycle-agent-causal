(define (domain goldminer)
  (:requirements :strips)
  (:predicates
    (robot-at ?loc)
    (clear ?loc)
    (holding-laser)
    (holding-bomb)
    (holding-gold)
    (arm-empty)
    (connected ?loc1 ?loc2)
    (soft-rock-at ?loc)
    (bomb-at ?loc)
    (laser-at ?loc)
    (gold-at ?loc)
  )
  
  (:action move
    :parameters (?from ?to)
    :precondition (and (robot-at ?from) (connected ?from ?to) (clear ?to))
    :effect (and (not (robot-at ?from)) (robot-at ?to))
  )

  (:action pick-up-laser
    :parameters (?loc)
    :precondition (and (robot-at ?loc) (laser-at ?loc) (arm-empty))
    :effect (and (not (arm-empty)) (holding-laser) (not (laser-at ?loc)))
  )

  (:action pick-up-bomb
    :parameters (?loc)
    :precondition (and (robot-at ?loc) (bomb-at ?loc) (arm-empty))
    :effect (and (not (arm-empty)) (holding-bomb) (not (bomb-at ?loc)))
  )

  (:action put-down-laser
    :parameters (?loc)
    :precondition (and (robot-at ?loc) (holding-laser))
    :effect (and (arm-empty) (laser-at ?loc) (not (holding-laser)))
  )

  (:action detonate-bomb
    :parameters (?locA ?locB)
    :precondition (and (robot-at ?locA) (holding-bomb) (connected ?locA ?locB) (soft-rock-at ?locB))
    :effect (and (arm-empty) (not (holding-bomb)) (not (soft-rock-at ?locB)) (clear ?locB))
  )

  (:action fire-laser
    :parameters (?locA ?locB)
    :precondition (and (robot-at ?locA) (holding-laser) (connected ?locA ?locB))
    :effect (and (clear ?locB) (not (soft-rock-at ?locB)) (not (gold-at ?locB)) (not (hard-rock-at ?locB)))
  )

  (:action pick-gold
    :parameters (?loc)
    :precondition (and (robot-at ?loc) (arm-empty) (gold-at ?loc))
    :effect (and (not (arm-empty)) (holding-gold) (not (gold-at ?loc)))
  )
)