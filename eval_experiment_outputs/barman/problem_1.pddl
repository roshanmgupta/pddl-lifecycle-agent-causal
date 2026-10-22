(define (problem barman_problem_1)
  (:domain barman)

  (:objects
    left - hand
    right - hand
    dispenser1 - dispenser
    dispenser2 - dispenser
    ingredient1 - ingredient
    ingredient2 - ingredient
    cocktail1 - cocktail
    glass1 - glass
    shaker1 - shaker
  )

  (:init
    (ontable glass1)
    (ontable shaker1)
    (handempty left)
    (handempty right)
    (clean glass1)
    (clean shaker1)
    (empty glass1)
    (empty shaker1)
    (dispenses dispenser1 ingredient1)
    (dispenses dispenser2 ingredient2)
    (cocktail_part1 cocktail1 ingredient1)
    (cocktail_part2 cocktail1 ingredient2)
  )

  (:goal (and (contains glass1 cocktail1)))
)