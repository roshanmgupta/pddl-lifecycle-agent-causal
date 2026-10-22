(define (problem freecell_problem)
  (:domain freecell)

  (:objects
    c1 - card
    c2 - card
    c3 - card
    v1 - value
    v2 - value
    v3 - value
    s1 - suit
    s2 - suit
    s3 - suit
    col1 - column
    col2 - column
    fc1 - freecell
    f1 - foundation
  )

  (:init
    (has_value c1 v1)
    (has_suit c1 s1)
    (has_value c2 v2)
    (has_suit c2 s2)
    (has_value c3 v3)
    (has_suit c3 s3)
    (on c1 c2)
    (on c2 c3)
    (clear c1)
    (empty_column col1)
    (empty_column col2)
    (empty_freecell fc1)
    (empty_foundation f1)
    (successor v1 v2)
    (successor v2 v3)
  )

  (:goal (and (in_foundation c1 f1) (in_foundation c2 f1) (in_foundation c3 f1)))
)