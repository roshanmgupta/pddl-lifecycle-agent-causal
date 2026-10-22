(define (problem group_blocks_problem)
  (:domain grid_block_grouping)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    red - color
    blue - color
    c1 - cell
    c2 - cell
    c3 - cell
    c4 - cell
  )

  (:init
    (block-color b1 red)
    (block-color b2 red)
    (block-color b3 blue)
    (block-color b4 blue)
    (at b1 c1)
    (at b2 c2)
    (at b3 c3)
    (at b4 c4)
    (adjacent c1 c2)
    (adjacent c2 c1)
    (adjacent c2 c3)
    (adjacent c3 c2)
    (adjacent c3 c4)
    (adjacent c4 c3)
    (adjacent c1 c3)
    (adjacent c3 c1)
    (adjacent c2 c4)
    (adjacent c4 c2)
  )

  (:goal (and (at b1 c1) (at b2 c1) (at b3 c2) (at b4 c2)))
)