(define (domain reachlunch_portfolio)
  (:requirements :strips :typing)

  (:types
    encoding problem solver - object
  )

  (:predicates
    (dfs_run ?p - problem)
    (encoded ?p - problem ?e - encoding)
    (solved ?p - problem)
  )

  (:action run_dfs
    :parameters (?p - problem)
    :precondition (and)
    :effect (dfs_run ?p)
  )

  (:action encode_compact_reinforced
    :parameters (?p - problem ?e - encoding)
    :precondition (dfs_run ?p)
    :effect (encoded ?p ?e)
  )

  (:action solve_ic3_pdr
    :parameters (?p - problem ?e - encoding ?s - solver)
    :precondition (encoded ?p ?e)
    :effect (solved ?p)
  )

)