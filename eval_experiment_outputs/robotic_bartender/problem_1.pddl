(define (problem make_martini)
  (:domain robotic_bartender)

  (:objects
    h1 - hand
    h2 - hand
    s1 - shot_glass
    sh1 - shaker
    cg1 - cocktail_glass
    d1 - dispenser
    d2 - dispenser
    i1 - ingredient
    i2 - ingredient
    sink1 - sink
  )

  (:init
    (hand_empty h1)
    (hand_empty h2)
    (clean_shot s1)
    (empty_shot s1)
    (clean_shaker sh1)
    (clean_glass cg1)
    (dispenser_clean d1)
    (dispenser_clean d2)
    (dispenser_has d1 i1)
    (dispenser_has d2 i2)
    (recipe sh1 i1)
    (recipe sh1 i2)
    (at h1 sink1)
    (at h2 sink1)
  )

  (:goal (and (ready cg1)))
)