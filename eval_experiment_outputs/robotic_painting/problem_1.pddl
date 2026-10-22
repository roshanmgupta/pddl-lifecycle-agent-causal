(define (problem paint_tiles)
  (:domain robotic_painting)

  (:objects
    r1 - robot
    t1 - tile
    t2 - tile
    t3 - tile
    t4 - tile
    ps1 - paint_station
    black - color
    white - color
  )

  (:init
    (at r1 t1)
    (adjacent t1 t2)
    (adjacent t2 t1)
    (adjacent t2 t3)
    (adjacent t3 t2)
    (adjacent t3 t4)
    (adjacent t4 t3)
    (unpainted t1)
    (unpainted t2)
    (unpainted t3)
    (unpainted t4)
    (current_color r1 black)
    (at_paint_station r1 ps1)
  )

  (:goal (and (painted t1 black) (painted t2 white) (painted t3 black) (painted t4 white)))
)