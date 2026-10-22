(define (problem block_stack_target)
  (:domain block_stacking)

  (:objects
    b1 - block
    b2 - block
    b3 - block
    b4 - block
    b5 - block
    table - location
  )

  (:init
    (at b1 table)
  )

  (:goal (and (at b1 loc_c) (at b2 loc_d) (at b3 loc_b) (at b4 loc_a) (at b5 loc_b3)))
)