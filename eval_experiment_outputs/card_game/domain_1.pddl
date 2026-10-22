(define (domain card_game)
  (:requirements :strips :typing)

  (:types
    card space suit value - object
  )

  (:predicates
    (clear ?c - card)
    (on ?c1 - card ?c2 - card)
    (bottom_color ?c - card)
    (can_stack ?c1 - card ?c2 - card)
    (successor ?v1 - value ?v2 - value)
    (cell_space ?s - space)
    (column_space ?s - space)
    (home ?c - card)
    (has_value ?c - card ?v - value)
    (has_suit ?c - card ?s - suit)
    (in_cell ?c - card)
  )

  (:action move_card
    :parameters (?a - card ?b - card ?c - card)
    :precondition (and (clear ?a) (clear ?c) (can_stack ?a ?c) (on ?a ?b))
    :effect (and (not (on ?a ?b)) (on ?a ?c) (clear ?b) (not (clear ?c)))
  )

  (:action move_card_to_column
    :parameters (?a - card ?b - card ?c - space ?d - value)
    :precondition (and (clear ?a) (bottom_color ?a) (clear ?b) (can_stack ?a ?b) (column_space ?c) (successor ?d ?c))
    :effect (and (not (bottom_color ?a)) (not (clear ?b)) (not (column_space ?c)) (on ?a ?b) (column_space ?d))
  )

  (:action send_card_to_cell
    :parameters (?a - card ?b - card ?c - space ?d - space)
    :precondition (and (clear ?a) (on ?a ?b) (cell_space ?c) (successor ?d ?c))
    :effect (and (not (on ?a ?b)) (not (clear ?a)) (not (cell_space ?c)) (in_cell ?a) (clear ?b) (cell_space ?d))
  )

  (:action send_card_to_free_cell
    :parameters (?a - card ?b - space ?c - space ?d - space ?e - space)
    :precondition (and (clear ?a) (bottom_color ?a) (cell_space ?b) (successor ?b ?c) (column_space ?d) (successor ?d ?e))
    :effect (and (not (bottom_color ?a)) (not (clear ?a)) (not (column_space ?d)) (not (cell_space ?b)) (in_cell ?a) (column_space ?e) (cell_space ?c))
  )

  (:action send_card_to_new_column
    :parameters (?a - card ?b - card ?c - space ?d - space)
    :precondition (and (clear ?a) (column_space ?c) (successor ?c ?d) (on ?a ?b))
    :effect (and (not (on ?a ?b)) (not (column_space ?c)) (bottom_color ?a) (clear ?b) (column_space ?d))
  )

  (:action send_card_to_home
    :parameters (?a - card ?b - card ?e - card ?c - suit ?d - value ?f - value)
    :precondition (and (clear ?a) (on ?a ?b) (home ?e) (has_suit ?a ?c) (has_suit ?e ?c) (has_value ?a ?d) (has_value ?e ?f) (successor ?f ?d))
    :effect (and (not (on ?a ?b)) (not (home ?e)) (not (clear ?a)) (home ?a) (clear ?b))
  )

  (:action send_card_to_home_from_column
    :parameters (?a - card ?b - suit ?c - value ?d - card ?e - value ?f - space ?g - space)
    :precondition (and (clear ?a) (bottom_color ?a) (home ?d) (has_suit ?a ?b) (has_suit ?d ?b) (has_value ?a ?c) (has_value ?d ?e) (successor ?e ?c) (column_space ?f) (successor ?f ?g))
    :effect (and (not (home ?d)) (not (clear ?a)) (not (bottom_color ?a)) (not (column_space ?f)) (home ?a) (column_space ?g))
  )

  (:action send_card_to_home_from_cell
    :parameters (?a - card ?b - suit ?c - value ?d - card ?e - value ?f - space ?g - space)
    :precondition (and (in_cell ?a) (home ?d) (has_suit ?a ?b) (has_suit ?d ?b) (has_value ?a ?c) (has_value ?d ?e) (successor ?e ?c) (cell_space ?f) (successor ?f ?g))
    :effect (and (not (in_cell ?a)) (not (cell_space ?f)) (not (home ?d)) (home ?a) (cell_space ?g))
  )

  (:action move_card_from_cell_to_stack
    :parameters (?a - card ?b - card ?c - space ?d - space)
    :precondition (and (in_cell ?a) (clear ?b) (can_stack ?a ?b) (cell_space ?c) (successor ?c ?d))
    :effect (and (not (in_cell ?a)) (not (cell_space ?c)) (not (clear ?b)) (cell_space ?d) (clear ?a) (on ?a ?b))
  )

  (:action move_card_from_cell_to_new_column
    :parameters (?a - card ?b - space ?c - space ?d - space ?e - space)
    :precondition (and (in_cell ?a) (column_space ?b) (cell_space ?d) (successor ?b ?c) (successor ?d ?e))
    :effect (and (not (in_cell ?a)) (not (column_space ?b)) (not (cell_space ?d)) (bottom_color ?a) (clear ?a) (column_space ?c) (cell_space ?e))
  )

)