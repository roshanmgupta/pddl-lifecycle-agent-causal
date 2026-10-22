(define (problem instance-1)
  (:domain blocksworld)

  (:objects
    a - block
    b - block
    c - block
    d - block
  )

  (:init
    (hand-empty)
    (on-table a)
    (on b c)
    (on-table c)
    (on-table d)
    (clear a)
    (clear b)
    (clear d)
  )

  (:goal (and (on c b)))
)