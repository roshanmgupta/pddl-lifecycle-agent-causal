(define (problem freecell_problem)
  (:domain freecell)

  (:objects
    c1 - card
    c2 - card
    c3 - card
    p1 - pile
    p2 - pile
    f1 - freecell
    f2 - foundation
  )

  (:init
    (top c1 p1)
    (top c2 p2)
    (empty_freecell f1)
    (empty_foundation f2)
  )

  (:goal (and (in_foundation c1 f2) (in_foundation c2 f2)))
)