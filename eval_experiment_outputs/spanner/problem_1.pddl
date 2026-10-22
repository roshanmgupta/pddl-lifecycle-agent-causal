(define (problem problem_gold)
  (:domain spanner)

  (:objects
    shed - location
    garden - location
    gate - location
    bob - man
    spanner1 - spanner
    nut1 - nut
  )

  (:init
    (link shed garden)
    (link garden shed)
    (link garden gate)
    (link gate garden)
    (at bob garden)
    (at spanner1 shed)
    (at nut1 gate)
    (loose nut1)
    (useable spanner1)
  )

  (:goal (and (tightened nut1)))
)