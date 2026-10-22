(define (problem instance-1)
  (:domain floortile)

  (:objects
    tile_0-1 - tile
    tile_0-2 - tile
    tile_1-1 - tile
    tile_1-2 - tile
    tile_2-1 - tile
    tile_2-2 - tile
    robot1 - robot
    robot2 - robot
    white - color
    black - color
  )

  (:init
    (at robot1 tile_1-2)
    (has robot1 white)
    (at robot2 tile_1-1)
    (has robot2 black)
    (available white)
    (available black)
    (clear tile_0-1)
    (clear tile_0-2)
    (clear tile_2-1)
    (clear tile_2-2)
    (up tile_1-1 tile_0-1)
    (up tile_1-2 tile_0-2)
    (up tile_2-1 tile_1-1)
    (up tile_2-2 tile_1-2)
    (down tile_0-1 tile_1-1)
    (down tile_0-2 tile_1-2)
    (down tile_1-1 tile_2-1)
    (down tile_1-2 tile_2-2)
    (right-of tile_0-2 tile_0-1)
    (right-of tile_1-2 tile_1-1)
    (right-of tile_2-2 tile_2-1)
    (left-of tile_0-1 tile_0-2)
    (left-of tile_1-1 tile_1-2)
    (left-of tile_2-1 tile_2-2)
  )

  (:goal (and (painted tile_1-1 white) (painted tile_1-2 black) (painted tile_2-1 black) (painted tile_2-2 white)))
)