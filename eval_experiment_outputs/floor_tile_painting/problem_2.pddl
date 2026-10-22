(define (problem paint_5x3_grid)
  (:domain floor_tile_painting)

  (:objects
    robot1 - robot
    robot2 - robot
    tile_0-1 - tile
    tile_0-2 - tile
    tile_0-3 - tile
    tile_1-1 - tile
    tile_1-2 - tile
    tile_1-3 - tile
    tile_2-1 - tile
    tile_2-2 - tile
    tile_2-3 - tile
    tile_3-1 - tile
    tile_3-2 - tile
    tile_3-3 - tile
    tile_4-1 - tile
    tile_4-2 - tile
    tile_4-3 - tile
    white - color
    black - color
  )

  (:init
    (at robot1 tile_2-3)
    (has_color robot1 white)
    (at robot2 tile_1-1)
    (has_color robot2 black)
    (clear tile_0-1)
    (clear tile_0-2)
    (clear tile_0-3)
    (clear tile_1-2)
    (clear tile_1-3)
    (clear tile_2-1)
    (clear tile_2-2)
    (clear tile_3-1)
    (clear tile_3-2)
    (clear tile_3-3)
    (clear tile_4-1)
    (clear tile_4-2)
    (clear tile_4-3)
    (up_of tile_0-1 tile_1-1)
    (up_of tile_0-2 tile_1-2)
    (up_of tile_0-3 tile_1-3)
    (up_of tile_1-1 tile_2-1)
    (up_of tile_1-2 tile_2-2)
    (up_of tile_1-3 tile_2-3)
    (up_of tile_2-1 tile_3-1)
    (up_of tile_2-2 tile_3-2)
    (up_of tile_2-3 tile_3-3)
    (up_of tile_3-1 tile_4-1)
    (up_of tile_3-2 tile_4-2)
    (up_of tile_3-3 tile_4-3)
    (down_of tile_1-1 tile_0-1)
    (down_of tile_1-2 tile_0-2)
    (down_of tile_1-3 tile_0-3)
    (down_of tile_2-1 tile_1-1)
    (down_of tile_2-2 tile_1-2)
    (down_of tile_2-3 tile_1-3)
    (down_of tile_3-1 tile_2-1)
    (down_of tile_3-2 tile_2-2)
    (down_of tile_3-3 tile_2-3)
    (down_of tile_4-1 tile_3-1)
    (down_of tile_4-2 tile_3-2)
    (down_of tile_4-3 tile_3-3)
    (left_of tile_0-1 tile_0-2)
    (left_of tile_0-2 tile_0-3)
    (left_of tile_1-1 tile_1-2)
    (left_of tile_1-2 tile_1-3)
    (left_of tile_2-1 tile_2-2)
    (left_of tile_2-2 tile_2-3)
    (left_of tile_3-1 tile_3-2)
    (left_of tile_3-2 tile_3-3)
    (left_of tile_4-1 tile_4-2)
    (left_of tile_4-2 tile_4-3)
    (right_of tile_0-2 tile_0-1)
    (right_of tile_0-3 tile_0-2)
    (right_of tile_1-2 tile_1-1)
    (right_of tile_1-3 tile_1-2)
    (right_of tile_2-2 tile_2-1)
    (right_of tile_2-3 tile_2-2)
    (right_of tile_3-2 tile_3-1)
    (right_of tile_3-3 tile_3-2)
    (right_of tile_4-2 tile_4-1)
    (right_of tile_4-3 tile_4-2)
  )

  (:goal (and (painted tile_1-1 white) (painted tile_1-2 black) (painted tile_1-3 white) (painted tile_2-1 black) (painted tile_2-2 white) (painted tile_2-3 black) (painted tile_3-1 white) (painted tile_3-2 black) (painted tile_3-3 white) (painted tile_4-1 black) (painted tile_4-2 white) (painted tile_4-3 black)))
)