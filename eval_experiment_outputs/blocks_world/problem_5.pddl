(define (problem blocks_world_problem)
  (:domain blocks_world)

  (:objects
    a1 - arm
    b1 - block
    b2 - block
    b3 - block
  )

  (:init
    (empty a1)
    (on_table b1)
    (on b2 b3)
    (clear b2)
    (on b3 b1)
  )

  (:goal (and (on b2 b3) (on b3 b1)))
)