(define (problem instance-3)
  (:domain blocksworld_scaled)

  (:objects
    b1 - object
    b2 - object
    b3 - object
    b4 - object
    b5 - object
    b6 - object
    b7 - object
    b8 - object
    b9 - object
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