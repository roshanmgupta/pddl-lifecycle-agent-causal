(define (problem instance-1)
  (:domain blocksworld)

  (:objects
    a - block
    b - block
    c - block
    d - block
  )

  (:init
    (handempty)
    (ontable a)
    (on b c)
    (ontable c)
    (ontable d)
    (clear a)
    (clear b)
    (clear d)
  )

  (:goal (and (on c b)))
)