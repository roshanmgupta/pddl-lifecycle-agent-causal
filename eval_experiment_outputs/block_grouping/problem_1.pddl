(define (problem group_blocks_by_color)
  (:domain block_grouping)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    c1 - cell
    c2 - cell
    c3 - cell
    c4 - cell
    red - color
    blue - color
  )

  (:init
    (has_color b1 red)
    (has_color b2 red)
    (has_color b3 blue)
    (has_color b4 blue)
    (at b1 c1)
    (at b2 c1)
    (at b3 c2)
    (at b4 c3)
    (adjacent c1 c2)
    (adjacent c2 c1)
    (adjacent c2 c3)
    (adjacent c3 c2)
    (adjacent c3 c4)
    (adjacent c4 c3)
  )

  (:goal (and (at b1 c2) (at b2 c2) (at b3 c4) (at b4 c4)))
)