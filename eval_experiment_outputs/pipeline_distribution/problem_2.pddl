(define (problem pipeline_problem)
  (:domain pipeline_distribution)

  (:objects
    pipe1 - pipe
    area1 - area
    area2 - area
    batch1 - batch_atom
    batch2 - batch_atom
    product1 - product
    product2 - product
  )

  (:init
    (connect area1 area2 pipe1)
    (on batch1 area1)
    (product_of batch1 product1)
    (product_of batch2 product2)
    (may_interface product1 product2)
    (on batch2 area1)
  )

  (:goal (and (on batch2 area2)))
)