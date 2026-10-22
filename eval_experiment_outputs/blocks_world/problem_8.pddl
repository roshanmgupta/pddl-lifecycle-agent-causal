(define (problem blocks_problem)
  (:domain blocks_world)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    arm1 - arm
  )

  (:init
    (empty arm1)
    (on-table b1)
    (on b2 b3)
    (clear b2)
    (on b3 b1)
  )

  (:goal (and (on b2 b3) (on b3 b1)))
)