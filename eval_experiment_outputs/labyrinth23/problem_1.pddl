(define (problem instance-1)
  (:domain labyrinth23)

  (:objects
    pos0 - gridpos
    pos1 - gridpos
    pos2 - gridpos
    card0 - card
    card1 - card
    card2 - card
    card3 - card
    card4 - card
    card5 - card
    card6 - card
    card7 - card
    card8 - card
    n - directionv
    s - directionv
    e - directionh
    w - directionh
  )

  (:init
    (maximum-position pos2)
    (minimum-position pos0)
    (next-to pos1 pos0)
    (next-to pos2 pos1)
    (card-at card0 pos0 pos0)
    (card-at card4 pos1 pos0)
    (card-at card2 pos2 pos0)
    (card-at card3 pos0 pos1)
    (card-at card7 pos1 pos1)
    (card-at card5 pos2 pos1)
    (card-at card6 pos0 pos2)
    (card-at card1 pos1 pos2)
    (card-at card8 pos2 pos2)
    (blocked card0 n)
    (blocked card4 w)
    (blocked card2 n)
    (blocked card3 n)
    (blocked card7 s)
    (blocked card7 w)
    (blocked card5 e)
    (blocked card6 e)
    (blocked card6 s)
    (blocked card1 n)
    (blocked card8 e)
    (robot-at card0)
  )

  (:goal (and (on-left)))
)