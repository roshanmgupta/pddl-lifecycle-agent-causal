(define (problem instance-1)
  (:domain barman14-bfs)

  (:objects
    shaker1 - shaker
    left right - hand
    shot1 shot2 shot3 shot4 shot5 - shot
    ingredient1 ingredient2 ingredient3 - ingredient
    cocktail1 cocktail2 cocktail3 cocktail4 - cocktail
    dispenser1 dispenser2 dispenser3 - dispenser
    l0 l1 l2 - level
    table - object
  )

  (:init
    (on shaker1 table)
    (on shot1 table)
    (on shot2 table)
    (on shot3 table)
    (on shot4 table)
    (on shot5 table)
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
    (empty left)
    (empty right)
    (at-level shaker1 l0)
    (at-level shaker1 l0)
    (next-to l0 l1)
    (next-to l1 l2)
    (part-of ingredient1 cocktail1)
    (part-of ingredient3 cocktail1)
    (part-of ingredient2 cocktail2)
    (part-of ingredient3 cocktail2)
    (part-of ingredient3 cocktail3)
    (part-of ingredient2 cocktail3)
    (part-of ingredient3 cocktail4)
    (part-of ingredient1 cocktail4)
  )

  (:goal (and (contains shot1 cocktail4) (contains shot2 cocktail2) (contains shot3 cocktail3) (contains shot4 cocktail1)))
)