(define (problem blocksworld_3blocks)
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
    (handempty)
  )

  (:goal (and (on c b) (on b a)))
)