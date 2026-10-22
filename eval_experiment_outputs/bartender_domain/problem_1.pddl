(define (problem bartender_problem)
  (:domain bartender_domain)

  (:objects
    hand1 - robot_hand
    hand2 - robot_hand
    shaker1 - shaker
    shot1 - container
    shot2 - container
    vodka - ingredient
    juice - ingredient
    vodka_dispenser - dispenser
    juice_dispenser - dispenser
    sink1 - sink
    glass1 - cocktail_glass
  )

  (:init
    (empty_hand hand1)
    (empty_hand hand2)
    (clean shaker1)
    (clean shot1)
    (clean shot2)
    (empty shaker1)
    (empty shot1)
    (empty shot2)
    (at_dispenser vodka_dispenser vodka)
    (at_dispenser juice_dispenser juice)
    (at_sink sink1)
  )

  (:goal (and (contains glass1 vodka) (contains glass1 juice)))
)