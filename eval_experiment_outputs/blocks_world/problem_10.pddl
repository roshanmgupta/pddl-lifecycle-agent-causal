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
    b10 - block
    b11 - block
    b12 - block
    arm1 - arm
  )

  (:init
    (empty arm1)
    (on b1 b12)
    (on-table b2)
    (on b3 b9)
    (on b4 b10)
    (on b5 b8)
    (clear b5)
    (on-table b6)
    (clear b6)
    (on-table b7)
    (clear b7)
    (on-table b8)
    (on b9 b1)
    (on b10 b3)
    (on b11 b4)
    (clear b11)
    (on b12 b2)
  )

  (:goal (and (on b1 b6) (on b5 b3) (on b6 b2) (on b8 b9) (on b9 b10) (on b10 b1) (on b11 b12) (on b12 b8)))
)