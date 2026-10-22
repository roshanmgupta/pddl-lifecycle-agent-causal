(define (domain hiking14)
  (:requirements :strips :typing)

  (:types
    car couple person place tent - object
  )

  (:predicates
    (partners ?a - person ?b - person ?c - couple)
    (at_person ?a - person ?p - place)
    (walked_to ?c - couple ?p - place)
    (at_tent ?t - tent ?p - place)
    (at_car ?c - car ?p - place)
    (next_to ?p1 - place ?p2 - place)
    (tent_up ?t - tent)
    (tent_down ?t - tent)
  )

  (:action put_down_tent
    :parameters (?a - person ?b - place ?c - tent)
    :precondition (and (at_person ?a ?b) (at_tent ?c ?b) (tent_up ?c))
    :effect (and (tent_down ?c) (not (tent_up ?c)))
  )

  (:action put_up_tent
    :parameters (?a - person ?b - place ?c - tent)
    :precondition (and (at_person ?a ?b) (at_tent ?c ?b) (tent_down ?c))
    :effect (and (tent_up ?c) (not (tent_down ?c)))
  )

  (:action drive_person_person
    :parameters (?a - person ?e - person ?b - place ?c - place ?d - car)
    :precondition (and (at_person ?a ?b) (at_car ?d ?b) (at_person ?e ?b) (not (= ?a ?e)))
    :effect (and (at_person ?a ?c) (at_car ?d ?c) (at_person ?e ?c) (not (at_person ?a ?b)) (not (at_car ?d ?b)) (not (at_person ?e ?b)))
  )

  (:action drive_person
    :parameters (?a - person ?b - place ?c - place ?d - car)
    :precondition (and (at_person ?a ?b) (at_car ?d ?b))
    :effect (and (at_person ?a ?c) (at_car ?d ?c) (not (at_person ?a ?b)) (not (at_car ?d ?b)))
  )

  (:action drive_person_with_tent
    :parameters (?a - person ?b - place ?c - place ?d - car ?e - tent)
    :precondition (and (at_person ?a ?b) (at_car ?d ?b) (at_tent ?e ?b) (tent_down ?e))
    :effect (and (at_person ?a ?c) (at_car ?d ?c) (at_tent ?e ?c) (not (at_person ?a ?b)) (not (at_car ?d ?b)) (not (at_tent ?e ?b)))
  )

  (:action drive_person_person_with_tent
    :parameters (?a - person ?f - person ?b - place ?c - place ?d - car ?e - tent)
    :precondition (and (at_person ?a ?b) (at_car ?d ?b) (at_tent ?e ?b) (tent_down ?e) (at_person ?f ?b) (not (= ?a ?f)))
    :effect (and (at_person ?a ?c) (at_car ?d ?c) (at_tent ?e ?c) (at_person ?f ?c) (not (at_person ?a ?b)) (not (at_car ?d ?b)) (not (at_tent ?e ?b)) (not (at_person ?f ?b)))
  )

  (:action walk_together
    :parameters (?d - place ?b - place ?a - tent ?c - person ?e - person ?f - couple)
    :precondition (and (at_tent ?a ?b) (tent_up ?a) (at_person ?c ?d) (next_to ?d ?b) (at_person ?e ?d) (walked_to ?f ?d) (partners ?c ?e ?f) (not (= ?c ?e)))
    :effect (and (at_person ?c ?b) (at_person ?e ?b) (walked_to ?f ?b) (not (at_person ?c ?d)) (not (at_person ?e ?d)) (not (walked_to ?f ?d)))
  )

)