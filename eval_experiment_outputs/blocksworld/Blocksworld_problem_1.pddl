(define (problem blocksworld_problem)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
  )

  (:init
    (on A B)
    (ontable B)
    (ontable C)
    (clear A)
    (clear C)
    (handempty)
  )

  (:goal (and (on C B) (on B A)))
)