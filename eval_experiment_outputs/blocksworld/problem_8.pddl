(define (problem blocksworld_scenario)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
  )

  (:init
    (on A B)
    (on-table B)
    (on-table C)
    (clear A)
    (clear C)
    (arm-empty)
  )

  (:goal (and (on C B) (on B A)))
)