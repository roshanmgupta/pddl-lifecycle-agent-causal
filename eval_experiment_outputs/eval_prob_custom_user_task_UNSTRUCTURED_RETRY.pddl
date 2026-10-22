(define (problem instance-1)
  (:domain barman11-bfs)
  (:objects 
    shaker1 - shaker
    left right - hand
    shot1 shot2 shot3 shot4 - shot
    ingredient1 ingredient2 ingredient3 - ingredient
    cocktail1 cocktail2 cocktail3 - cocktail
    dispenser1 dispenser2 dispenser3 - dispenser
    l0 l1 l2 - level
  )
  (:init 
    (on-table shaker1)
    (on-table shot1)
    (on-table shot2)
    (on-table shot3)
    (on-table shot4)
    (dispenses dispenser1 ingredient1)
    (dispenses dispenser2 ingredient2)
    (dispenses dispenser3 ingredient3)
    (clean shaker1)
    (clean shot1)
    (clean shot2)
    (clean shot3)
    (clean shot4)
    (empty shaker1)
    (empty shot1)
    (empty shot2)
    (empty shot3)
    (empty shot4)
    (empty left)
    (empty right)
    (at-level shaker1 l0)
    (next-to l0 l1)
    (next-to l1 l2)
    (used-by shot1 ingredient3)
    (used-by shot1 ingredient1)
    (used-by shot2 ingredient2)
    (used-by shot2 ingredient3)
    (used-by shot3 ingredient1)
    (used-by shot3 ingredient2)
  )
  (:goal 
    (and 
      (contains shot1 cocktail3)
      (contains shot2 cocktail1)
      (contains shot3 cocktail2)
    )
  )
)