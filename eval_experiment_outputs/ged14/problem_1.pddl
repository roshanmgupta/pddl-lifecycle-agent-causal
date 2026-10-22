(define (problem instance-1)
  (:domain ged14)

  (:objects
    SUB1 - gene
    SUB2 - gene
    SUB3 - gene
  )

  (:init
    (normal SUB2)
    (normal SUB3)
    (normal SUB1)
    (present SUB2)
    (present SUB3)
    (present SUB1)
    (clockwise SUB1 SUB2)
    (clockwise SUB3 SUB1)
    (clockwise SUB2 SUB3)
    (idle)
  )

  (:goal (and (normal SUB2) (inverted SUB3) (normal SUB1) (clockwise SUB1 SUB2) (clockwise SUB3 SUB1) (clockwise SUB2 SUB3)))
)