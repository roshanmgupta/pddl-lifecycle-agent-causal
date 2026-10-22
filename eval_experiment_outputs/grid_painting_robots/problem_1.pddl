(define (problem paint_corner_pattern)
  (:domain grid_painting_robots)

  (:objects
    r1 - robot
    white - color
    black - color
    up - direction
    down - direction
    left - direction
    right - direction
    t00 - tile
    t01 - tile
    t02 - tile
    t10 - tile
    t11 - tile
    t12 - tile
    t20 - tile
    t21 - tile
    t22 - tile
  )

  (:init
    (at r1 t00)
    (facing r1 right)
    (active_color r1 white)
    (has_sprayer r1 white)
    (has_sprayer r1 black)
    (paint_station t00)
    (clear t01)
    (clear t02)
    (clear t10)
    (clear t11)
    (clear t12)
    (clear t20)
    (clear t21)
    (clear t22)
    (opposite up down)
    (opposite down up)
    (opposite left right)
    (opposite right left)
    (adjacent t00 t01 right)
    (adjacent t01 t00 left)
    (adjacent t01 t02 right)
    (adjacent t02 t01 left)
    (adjacent t10 t11 right)
    (adjacent t11 t10 left)
    (adjacent t11 t12 right)
    (adjacent t12 t11 left)
    (adjacent t20 t21 right)
    (adjacent t21 t20 left)
    (adjacent t21 t22 right)
    (adjacent t22 t21 left)
    (adjacent t00 t10 down)
    (adjacent t10 t00 up)
    (adjacent t10 t20 down)
    (adjacent t20 t10 up)
    (adjacent t01 t11 down)
    (adjacent t11 t01 up)
    (adjacent t11 t21 down)
    (adjacent t21 t11 up)
    (adjacent t02 t12 down)
    (adjacent t12 t02 up)
    (adjacent t12 t22 down)
    (adjacent t22 t12 up)
  )

  (:goal (and (painted t01) (painted_with t01 white) (painted t02) (painted_with t02 black)))
)