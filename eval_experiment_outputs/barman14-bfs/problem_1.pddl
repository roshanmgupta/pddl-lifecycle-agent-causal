(define (problem instance-1)
  (:domain barman14-bfs)

  (:objects
    shaker1 - shaker
    left - hand
    right - hand
    shot1 - shot
    shot2 - shot
    shot3 - shot
    shot4 - shot
    shot5 - shot
    ingredient1 - ingredient
    ingredient2 - ingredient
    ingredient3 - ingredient
    cocktail1 - cocktail
    cocktail2 - cocktail
    cocktail3 - cocktail
    cocktail4 - cocktail
    dispenser1 - dispenser
    dispenser2 - dispenser
    dispenser3 - dispenser
    l0 - level
    l1 - level
    l2 - level
  )

  (:init
    (on-table shaker1)
    (on-table shot1)
    (on-table shot2)
    (on-table shot3)
    (on-table shot4)
    (on-table shot5)
    (dispenses dispenser1 ingredient1)
    (dispenses dispenser2 ingredient2)
    (dispenses dispenser3 ingredient3)
    (clean shaker1)
    (clean shot1)
    (clean shot2)
    (clean shot3)
    (clean shot4)
    (clean shot5)
    (empty shaker1)
    (empty shot1)
    (empty shot2)
    (empty shot3)
    (empty shot4)
    (empty shot5)
    (hand-empty left)
    (hand-empty right)
    (at-empty-level shaker1 l0)
    (at-level shaker1 l0)
    (next-to l0 l1)
    (next-to l1 l2)
    (part-of cocktail1 ingredient3)
    (another-part-of cocktail1 ingredient1)
    (part-of cocktail2 ingredient2)
    (another-part-of cocktail2 ingredient3)
    (part-of cocktail3 ingredient3)
    (another-part-of cocktail3 ingredient2)
    (part-of cocktail4 ingredient3)
    (another-part-of cocktail4 ingredient1)
  )

  (:goal (and (contains shot1 cocktail4) (contains shot2 cocktail2) (contains shot3 cocktail3) (contains shot4 cocktail1)))
)