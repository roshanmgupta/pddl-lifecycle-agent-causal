(define (problem blocksworld_problem)
  (:domain blocksworld)

  (:objects
    a - block
    b - block
    c - block
  )

  (:init
    (on a b)
    (ontable b)
    (ontable c)
    (clear a)
    (clear c)
    (arm-empty)
  )

  (:goal (and (on c b) (on b a)))
)