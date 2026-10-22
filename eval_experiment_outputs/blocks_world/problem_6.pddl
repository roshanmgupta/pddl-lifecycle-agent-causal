(define (problem blocks_world_problem)
  (:domain blocks_world)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    table - table
    arm - arm
  )

  (:init
    (empty arm)
    (on b1 b3)
    (clear b1)
    (on_table b2)
    (on b3 b2)
    (on_table b4)
    (clear b4)
  )

  (:goal (and (on b2 b1) (on b3 b4)))
)