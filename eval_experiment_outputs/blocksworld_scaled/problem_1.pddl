(define (problem instance-3)
  (:domain blocksworld_scaled)

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
  )

  (:init
    (hand-empty)
    (on b1 b5)
    (on b2 b8)
    (on b3 b6)
    (on b4 b7)
    (on-table b5)
    (on b6 b9)
    (on b7 b3)
    (on-table b8)
    (on-table b9)
    (clear b1)
    (clear b2)
    (clear b4)
  )

  (:goal (and (on b3 b9) (on b4 b5) (on b5 b8) (on b7 b3) (on b8 b1) (on b9 b2)))
)