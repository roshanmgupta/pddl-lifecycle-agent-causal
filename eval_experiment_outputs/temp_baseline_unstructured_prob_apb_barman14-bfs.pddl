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
    (empty left)
    (empty right)
    (next-to l0 l1)
    (next-to l1 l2)
    (part-of cocktail1 ingredient3)
    (part-of cocktail1 ingredient1)
    (part-of cocktail2 ingredient2)
    (part-of cocktail2 ingredient3)
    (part-of cocktail3 ingredient3)
    (part-of cocktail3 ingredient2)
    (part-of cocktail4 ingredient3)
    (part-of cocktail4 ingredient1)
  )
  
  (:goal 
    (and 
      (contains shot1 cocktail4)
      (contains shot2 cocktail2)
      (contains shot3 cocktail3)
      (contains shot4 cocktail1)
    )
  )
)