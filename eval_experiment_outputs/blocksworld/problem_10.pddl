(define (problem blocksworld_tower)
  (:domain blocksworld)

  (:objects
    A - block
    B - block
    C - block
    D - block
    E - block
  )

  (:init
    (on A B)
    (on-table B)
    (on D C)
    (on-table C)
    (on-table E)
    (clear A)
    (clear D)
    (clear E)
    (arm-empty)
  )

  (:goal (and (on A B) (on B C) (on C D) (on D E) (on-table E)))
)