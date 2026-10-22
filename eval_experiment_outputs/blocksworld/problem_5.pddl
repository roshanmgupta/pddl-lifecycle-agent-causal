(define (problem blocksworld-problem)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
    r1 - robot
  )

  (:init
    (on A B)
    (on-table B)
    (on-table C)
    (hand-empty r1)
    (clear A)
    (clear C)
  )

  (:goal (and (on C B) (on B A)))
)