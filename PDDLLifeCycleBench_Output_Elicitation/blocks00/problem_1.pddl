(define (problem instance-1.pddl)
  (:domain blocks00)

  (:objects
    D - object
    A - object
    H - object
    G - object
    B - object
    J - object
    E - object
    I - object
    F - object
    C - object
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