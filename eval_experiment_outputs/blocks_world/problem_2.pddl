(define (problem blocks_world_problem)
  (:domain blocks_world)

  (:objects
    block_a - block
    block_b - block
    block_c - block
  )

  (:init
    (ontable block_a)
    (ontable block_b)
    (ontable block_c)
    (clear block_a)
    (clear block_b)
    (clear block_c)
    (handempty)
  )

  (:goal (and (on block_a block_b) (on block_b block_c)))
)