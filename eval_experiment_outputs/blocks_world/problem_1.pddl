(define (problem blocks_problem_1)
  (:domain blocks_world)

  (:objects
    a - block
    b - block
    c - block
    t1 - table
  )

  (:init
    (ontable a)
    (ontable b)
    (ontable c)
    (clear a)
    (clear b)
    (clear c)
    (arm-empty)
  )

  (:goal (and (on a b) (on b c)))
)