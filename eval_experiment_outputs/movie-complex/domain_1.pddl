(define (domain movie-complex)
  (:requirements :strips :typing)

  (:types
    object snack - object
  )

  (:predicates
    (is_chips ?s - snack)
    (is_dip ?s - snack)
    (is_popped ?s - snack)
    (is_cheese ?s - snack)
    (is_crackers ?s - snack)
    (counter_at_zero)
    (counter_at_other_than_zero)
    (movie_rewound)
    (have_chips)
    (have_dip)
    (have_pop)
    (have_cheese)
    (have_crackers)
  )

  (:action rewind_movie
    :parameters ()
    :precondition (counter_at_other_than_zero)
    :effect (and (movie_rewound) (not (counter_at_other_than_zero)) (counter_at_zero))
  )

  (:action reset_counter
    :parameters ()
    :precondition (counter_at_other_than_zero)
    :effect (and (counter_at_zero) (not (counter_at_other_than_zero)))
  )

  (:action start_movie
    :parameters ()
    :precondition (counter_at_zero)
    :effect (and (counter_at_other_than_zero) (not (counter_at_zero)))
  )

  (:action undo_rewind
    :parameters ()
    :precondition (movie_rewound)
    :effect (not (movie_rewound))
  )

  (:action get_chips
    :parameters (?a - snack)
    :precondition (and (is_chips ?a) (counter_at_zero) (not (movie_rewound)))
    :effect (have_chips)
  )

  (:action get_dip
    :parameters (?a - snack)
    :precondition (and (is_dip ?a) (counter_at_zero) (not (movie_rewound)))
    :effect (have_dip)
  )

  (:action get_popped
    :parameters (?a - snack)
    :precondition (and (is_popped ?a) (counter_at_zero) (not (movie_rewound)))
    :effect (have_pop)
  )

  (:action get_cheese
    :parameters (?a - snack)
    :precondition (and (is_cheese ?a) (counter_at_zero) (not (movie_rewound)))
    :effect (have_cheese)
  )

  (:action get_crackers
    :parameters (?a - snack)
    :precondition (and (is_crackers ?a) (counter_at_zero) (not (movie_rewound)))
    :effect (have_crackers)
  )

)