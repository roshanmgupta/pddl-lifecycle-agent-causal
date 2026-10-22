(define (problem blocks_world_problem)
  (:domain blocks_world)

  (:objects
    a - block
    b - block
    c - block
  )

  (:init
    (ontable a)
    (ontable b)
    (on c a)
    (clear b)
    (clear c)
    (handempty)
  )

  (:goal (and (on a b) (on b c)))
)