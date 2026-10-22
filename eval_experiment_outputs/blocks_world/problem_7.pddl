(define (problem blocks_world_problem)
  (:domain blocks_world)

  (:objects
    a1 - arm
    t1 - table
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    b5 - block
    b6 - block
  )

  (:init
    (empty a1)
    (ontable b1 t1)
    (on b2 b3)
    (on b3 b1)
    (ontable b4 t1)
    (clear b4)
    (on b5 b2)
    (clear b5)
    (ontable b6 t1)
    (clear b6)
  )

  (:goal (and (on b3 b5) (on b4 b3)))
)