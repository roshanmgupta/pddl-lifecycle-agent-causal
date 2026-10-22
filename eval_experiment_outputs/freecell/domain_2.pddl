(define (domain freecell)
  (:requirements :strips :typing)

  (:types
    card column foundation freecell suit value - object
  )

  (:predicates
    (has_value ?c - card ?v - value)
    (has_suit ?c - card ?s - suit)
    (on ?c1 - card ?c2 - card)
    (clear ?c - card)
    (empty_column ?col - column)
    (canstack ?c1 - card ?c2 - card)
    (in_freecell ?c - card ?fc - freecell)
    (in_foundation ?c - card ?f - foundation)
    (successor ?v1 - value ?v2 - value)
    (empty_freecell ?fc - freecell)
    (empty_foundation ?f - foundation)
  )

  (:action move_to_column
    :parameters (?c - card ?from_col - column ?to_col - column ?top_card - card)
    :precondition (and (on ?c ?top_card) (clear ?c) (canstack ?c ?top_card) (empty_column ?to_col))
    :effect (and (not (on ?c ?top_card)) (not (clear ?c)) (clear ?top_card) (on ?c ?top_card) (not (empty_column ?to_col)))
  )

  (:action move_to_freecell
    :parameters (?c - card ?fc - freecell)
    :precondition (and (clear ?c) (empty_freecell ?fc))
    :effect (and (not (clear ?c)) (in_freecell ?c ?fc) (not (empty_freecell ?fc)))
  )

  (:action move_to_foundation
    :parameters (?c - card ?f - foundation ?v - value ?s - suit ?prev_card - card ?prev_v - value)
    :precondition (and (clear ?c) (has_value ?c ?v) (has_suit ?c ?s) (in_foundation ?prev_card ?f) (has_value ?prev_card ?prev_v) (successor ?prev_v ?v))
    :effect (and (not (clear ?c)) (in_foundation ?c ?f) (clear ?prev_card))
  )

  (:action initialize_foundation
    :parameters (?f - foundation ?c - card ?v - value ?s - suit)
    :precondition (and (empty_foundation ?f) (clear ?c) (has_value ?c ?v) (has_suit ?c ?s))
    :effect (and (not (empty_foundation ?f)) (in_foundation ?c ?f))
  )

  (:action make_card_clear
    :parameters (?c - card)
    :precondition (and)
    :effect (clear ?c)
  )

)