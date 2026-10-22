(define (domain grid_block_grouping)
  (:requirements :strips :typing)

  (:types
    block cell color - object
  )

  (:predicates
    (at ?b - block ?c - cell)
    (block-color ?b - block ?col - color)
    (adjacent ?c1 - cell ?c2 - cell)
  )

  (:action move
    :parameters (?b - block ?from - cell ?to - cell)
    :precondition (and (at ?b ?from) (adjacent ?from ?to))
    :effect (and (not (at ?b ?from)) (at ?b ?to))
  )

)