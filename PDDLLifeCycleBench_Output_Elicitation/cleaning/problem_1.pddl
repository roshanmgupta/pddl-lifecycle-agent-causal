(define (problem problem_gold)
  (:domain cleaning)

  (:objects
    robo - robot
    t1 t2 t3 - tile
  )

  (:init
    (robot-at robo t1)
    (clear t2)
    (clear t3)
    (cleaned t1)
    (cleaned t2)
    (cleaned t3)
    (left t1 t2)
    (right t2 t1)
    (right t3 t2)
    (left t2 t3)
  )

  (:goal (and (cleaned t2)))
)