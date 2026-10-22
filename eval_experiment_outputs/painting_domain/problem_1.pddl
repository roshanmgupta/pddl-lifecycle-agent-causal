(define (problem painting_problem)
  (:domain painting_domain)

  (:objects
    r1 - robot
    t1 - tile
    t2 - tile
    t3 - tile
    t4 - tile
    red - color
    blue - color
  )

  (:init
    (at r1 t1)
    (has r1 red)
    (has r1 blue)
    (clear t1)
    (clear t2)
    (clear t3)
    (clear t4)
    (up t2 t1)
    (down t3 t1)
    (left t4 t1)
    (right t1 t4)
  )

  (:goal (and (painted t2 red) (painted t3 blue) (painted t4 red)))
)