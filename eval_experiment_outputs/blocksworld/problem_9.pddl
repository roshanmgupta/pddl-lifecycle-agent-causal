(define (problem blocksworld_tower)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
    D - block
  )

  (:init
    (on A B)
    (on-table B)
    (on D C)
    (on-table C)
    (clear A)
    (clear D)
    (arm-empty)
  )

  (:goal (and (on A B) (on B C) (on C D) (on-table D)))
)