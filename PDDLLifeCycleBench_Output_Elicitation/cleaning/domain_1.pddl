(define (domain cleaning)
  (:requirements :strips :typing)

  (:types
    robot tile - object
  )

  (:predicates
    (robot-at ?robot - robot ?tile - tile)
    (clear ?tile - tile)
    (cleaned ?tile - tile)
    (left ?tile1 - tile ?tile2 - tile)
    (right ?tile1 - tile ?tile2 - tile)
  )

  (:action clean-up
    :parameters (?robot - robot ?robotTile - tile ?tileToBeCleaned - tile)
    :precondition (and (robot-at ?robot ?robotTile) (clear ?tileToBeCleaned))
    :effect (and (not (clear ?tileToBeCleaned)) (cleaned ?tileToBeCleaned))
  )

  (:action clean-down
    :parameters (?robot - robot ?robotTile - tile ?tileToBeCleaned - tile)
    :precondition (and (robot-at ?robot ?robotTile) (cleaned ?tileToBeCleaned))
    :effect (and (not (cleaned ?tileToBeCleaned)) (clear ?tileToBeCleaned))
  )

  (:action up
    :parameters (?robot - robot ?robotTile - tile ?moveToNextTile - tile)
    :precondition (and (robot-at ?robot ?robotTile) (left ?robotTile ?moveToNextTile))
    :effect (and (not (robot-at ?robot ?robotTile)) (robot-at ?robot ?moveToNextTile))
  )

  (:action down
    :parameters (?robot - robot ?robotTile - tile ?moveToNextTile - tile)
    :precondition (and (robot-at ?robot ?robotTile) (right ?robotTile ?moveToNextTile))
    :effect (and (not (robot-at ?robot ?robotTile)) (robot-at ?robot ?moveToNextTile))
  )

  (:action right
    :parameters (?robot - robot ?robotTile - tile ?moveToNextTile - tile)
    :precondition (and (robot-at ?robot ?robotTile) (right ?robotTile ?moveToNextTile))
    :effect (and (not (robot-at ?robot ?robotTile)) (robot-at ?robot ?moveToNextTile))
  )

  (:action left
    :parameters (?robot - robot ?robotTile - tile ?moveToNextTile - tile)
    :precondition (and (robot-at ?robot ?robotTile) (left ?robotTile ?moveToNextTile))
    :effect (and (not (robot-at ?robot ?robotTile)) (robot-at ?robot ?moveToNextTile))
  )

)