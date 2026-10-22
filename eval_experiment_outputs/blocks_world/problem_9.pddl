(define (problem blocks_problem)
  (:domain blocks_world)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    b5 - block
    b6 - block
    b7 - block
    b8 - block
    b9 - block
    arm1 - arm
  )

  (:init
    (empty arm1)
    (on b1 b3)
    (on-table b2)
    (on-table b3)
    (on b4 b6)
    (clear b4)
    (on b5 b1)
    (clear b5)
    (on-table b6)
    (on b7 b2)
    (on b8 b9)
    (clear b8)
    (on b9 b7)
  )

  (:goal (and (on b1 b2) (on b2 b7) (on b3 b5) (on b4 b1) (on b5 b6) (on b7 b8) (on b8 b3) (on b9 b4)))
)