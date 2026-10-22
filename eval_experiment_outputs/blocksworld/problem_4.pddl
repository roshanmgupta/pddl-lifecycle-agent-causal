(define (problem blocksworld-problem)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
  )

  (:init
    (on A B)
    (on-table B)
    (on-table C)
    (clear A)
    (clear C)
    (handempty)
  )

  (:goal (and (on C B) (on B A)))
)