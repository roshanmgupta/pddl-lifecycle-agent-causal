(define (problem instance-1)
  (:domain movie-complex)

  (:objects
    c1 - snack
    d1 - snack
    p1 - snack
    z1 - snack
    k1 - snack
  )

  (:init
    (is_chips c1)
    (is_dip d1)
    (is_popped p1)
    (is_cheese z1)
    (is_crackers k1)
    (counter_at_zero)
  )

  (:goal (and (movie_rewound) (counter_at_zero) (have_dip)))
)