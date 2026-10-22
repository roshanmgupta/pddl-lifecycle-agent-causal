(define (problem blocksworld_problem)
  (:domain blocksworld)

  (:objects
    a - block
    b - block
    c - block
    table - object
  )

  (:init
    (on a b)
    (ontable b)
    (ontable c)
    (arm-empty)
    (clear a)
  )

  (:goal (and (on c b) (on b a)))
)