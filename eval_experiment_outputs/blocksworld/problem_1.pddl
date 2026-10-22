(define (problem blocksworld_prob_01)
  (:domain blocksworld)

  (:objects
    a - block
    b - block
  )

  (:init
    (ontable a)
    (ontable b)
    (clear a)
    (clear b)
    (handempty)
  )

  (:goal (and (holding a)))
)