(define (domain hiking14)
  (:requirements :strips :typing)

  (:types
    car couple person place tent - object
  )

  (:predicates
    (partners ?a - person ?b - person ?c - couple)
    (at-person ?a - person ?p - place)
    (walked-to ?c - couple ?p - place)
    (at-tent ?t - tent ?p - place)
    (at-car ?c - car ?p - place)
    (next-to ?p1 - place ?p2 - place)
    (tent-up ?t - tent)
    (tent-down ?t - tent)
  )

  (:action put-down-tent
    :parameters (?a - person ?b - place ?c - tent)
    :precondition (and (at-person ?a ?b) (at-tent ?c ?b) (tent-up ?c))
    :effect (and (tent-down ?c) (not (tent-up ?c)))
  )

  (:action put-up-tent
    :parameters (?a - person ?b - place ?c - tent)
    :precondition (and (at-person ?a ?b) (at-tent ?c ?b) (tent-down ?c))
    :effect (and (tent-up ?c) (not (tent-down ?c)))
  )

  (:action drive-person-person
    :parameters (?a - person ?e - person ?b - place ?c - place ?d - car)
    :precondition (and (at-person ?a ?b) (at-car ?d ?b) (at-person ?e ?b) (not (= ?a ?e)))
    :effect (and (at-person ?a ?c) (at-car ?d ?c) (at-person ?e ?c) (not (at-person ?a ?b)) (not (at-car ?d ?b)) (not (at-person ?e ?b)))
  )

  (:action drive-person
    :parameters (?a - person ?b - place ?c - place ?d - car)
    :precondition (and (at-person ?a ?b) (at-car ?d ?b))
    :effect (and (at-person ?a ?c) (at-car ?d ?c) (not (at-person ?a ?b)) (not (at-car ?d ?b)))
  )

  (:action drive-person-tent
    :parameters (?a - person ?b - place ?c - place ?d - car ?e - tent)
    :precondition (and (at-person ?a ?b) (at-car ?d ?b) (at-tent ?e ?b) (tent-down ?e))
    :effect (and (at-person ?a ?c) (at-car ?d ?c) (at-tent ?e ?c) (not (at-person ?a ?b)) (not (at-car ?d ?b)) (not (at-tent ?e ?b)))
  )

  (:action drive-person-person-tent
    :parameters (?a - person ?f - person ?b - place ?c - place ?d - car ?e - tent)
    :precondition (and (at-person ?a ?b) (at-car ?d ?b) (at-tent ?e ?b) (tent-down ?e) (at-person ?f ?b) (not (= ?a ?f)))
    :effect (and (at-person ?a ?c) (at-car ?d ?c) (at-tent ?e ?c) (at-person ?f ?c) (not (at-person ?a ?b)) (not (at-car ?d ?b)) (not (at-tent ?e ?b)) (not (at-person ?f ?b)))
  )

  (:action walk-together
    :parameters (?a - tent ?c - person ?e - person ?f - couple ?d - place ?b - place)
    :precondition (and (at-tent ?a ?b) (tent-up ?a) (at-person ?c ?d) (next-to ?d ?b) (at-person ?e ?d) (walked-to ?f ?d) (partners ?c ?e ?f) (not (= ?c ?e)))
    :effect (and (at-person ?c ?b) (at-person ?e ?b) (walked-to ?f ?b) (not (at-person ?c ?d)) (not (at-person ?e ?d)) (not (walked-to ?f ?d)))
  )

)