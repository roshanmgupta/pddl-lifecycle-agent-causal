(define (problem block_stacking)
  (:domain block_world)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    b5 - block
    robot - robot
    table - table
  )

  (:init
    (on b3 b2)
    (on b2 b5)
    (on b5 b1)
    (on b1 b4)
    (on b4 table)
    (clear b3)
    (at robot table)
    (handempty robot)
  )

  (:goal (and (on b4 b3)))
)