(define (domain parking_lot)
  (:requirements :strips :typing)

  (:types
    car curb - object
  )

  (:predicates
    (at ?c - car ?loc - object)
    (behind ?c1 - car ?c2 - car)
    (clear ?c - car)
    (clear_curb ?curb - curb)
  )

  (:action move_curb_to_curb
    :parameters (?a - car ?b - curb ?c - curb)
    :precondition (and (clear ?a) (clear_curb ?c) (at ?a ?b))
    :effect (and (not (at ?a ?b)) (at ?a ?c) (clear_curb ?b) (not (clear_curb ?c)))
  )

  (:action move_curb_to_behind
    :parameters (?a - car ?b - curb ?c - car)
    :precondition (and (clear ?a) (clear ?c) (at ?a ?b) (at ?c ?b))
    :effect (and (not (at ?a ?b)) (behind ?a ?c) (clear_curb ?b) (not (clear ?c)))
  )

  (:action move_behind_to_curb
    :parameters (?a - car ?b - car ?c - curb)
    :precondition (and (clear ?a) (clear_curb ?c) (behind ?a ?b))
    :effect (and (not (behind ?a ?b)) (at ?a ?c) (clear ?b) (not (clear_curb ?c)))
  )

  (:action move_behind_to_behind
    :parameters (?a - car ?b - car ?c - car)
    :precondition (and (clear ?a) (clear ?c) (behind ?a ?b) (at ?c ?b))
    :effect (and (not (behind ?a ?b)) (behind ?a ?c) (clear ?b) (not (clear ?c)))
  )

)