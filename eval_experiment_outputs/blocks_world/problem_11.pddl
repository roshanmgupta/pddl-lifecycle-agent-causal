(define (problem instance-1)
  (:domain blocks_world)

  (:objects
    D - block
    A - block
    H - block
    G - block
    B - block
    J - block
    E - block
    I - block
    F - block
    C - block
  )

  (:init
    (clear C)
    (clear F)
    (on-table I)
    (on-table F)
    (on C E)
    (on E J)
    (on J B)
    (on B G)
    (on G H)
    (on H A)
    (on A D)
    (on D I)
    (hand-empty)
  )

  (:goal (and (on D C) (on C F) (on F J) (on J E) (on E H) (on H B) (on B A) (on A G) (on G I)))
)