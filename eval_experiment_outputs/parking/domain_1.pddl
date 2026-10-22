(define (domain parking)
  (:requirements :strips :typing)

  (:types
    car curb - object
  )

  (:predicates
    (at-curb ?c - car)
    (at-curb-number ?c - car ?cu - curb)
    (behind ?c1 - car ?c2 - car)
    (clear ?c - car)
    (clear-curb ?cu - curb)
  )

  (:action move-curb-to-curb
    :parameters (?a - car ?b - curb ?c - curb)
    :precondition (and (clear ?a) (clear-curb ?c) (at-curb-number ?a ?b))
    :effect (and (clear-curb ?b) (at-curb-number ?a ?c) (not (clear-curb ?c)) (not (at-curb-number ?a ?b)))
  )

  (:action move-curb-to-behind
    :parameters (?a - car ?b - curb ?c - car)
    :precondition (and (clear ?a) (clear ?c) (at-curb-number ?a ?b) (at-curb ?c))
    :effect (and (clear-curb ?b) (behind ?a ?c) (not (clear ?c)) (not (at-curb-number ?a ?b)) (not (at-curb ?a)))
  )

  (:action move-behind-to-curb
    :parameters (?a - car ?b - car ?c - curb)
    :precondition (and (clear ?a) (clear-curb ?c) (behind ?a ?b))
    :effect (and (clear ?b) (at-curb-number ?a ?c) (at-curb ?a) (not (clear-curb ?c)) (not (behind ?a ?b)))
  )

  (:action move-behind-to-behind
    :parameters (?a - car ?b - car ?c - car)
    :precondition (and (clear ?a) (clear ?c) (behind ?a ?b) (at-curb ?c))
    :effect (and (clear ?b) (behind ?a ?c) (not (clear ?c)) (not (behind ?a ?b)))
  )

)