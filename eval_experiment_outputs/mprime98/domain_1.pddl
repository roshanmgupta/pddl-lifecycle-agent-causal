(define (domain mprime98)
  (:requirements :strips :typing)

  (:types
    food object pain planet pleasure province - object
  )

  (:predicates
    (is_food ?x - object)
    (is_pleasure ?x - object)
    (is_pain ?x - object)
    (is_province ?x - object)
    (is_planet ?x - object)
    (craves ?x - object ?y - object)
    (eats ?x - object ?y - object)
    (located_in ?x - object ?y - object)
    (in_harmony_with ?x - object ?y - object)
    (orbits ?x - object ?y - object)
    (attacks ?x - object ?y - object)
    (fears ?x - object ?y - object)
  )

  (:action overcome_pain_with_pleasure
    :parameters (?a - pain ?b - pleasure ?c - food ?d - planet ?e - planet)
    :precondition (and (is_pain ?a) (is_pleasure ?b) (craves ?a ?c) (craves ?b ?c) (is_food ?c) (in_harmony_with ?b ?e) (is_planet ?e) (orbits ?d ?e) (is_planet ?d))
    :effect (and (fears ?a ?b) (in_harmony_with ?b ?d) (not (craves ?a ?c)) (not (in_harmony_with ?b ?e)))
  )

  (:action feast_with_pleasure
    :parameters (?a - pleasure ?b - food ?c - food ?d - province ?e - province)
    :precondition (and (craves ?a ?b) (is_food ?b) (is_pleasure ?a) (eats ?b ?c) (is_food ?c) (located_in ?b ?e) (attacks ?d ?e))
    :effect (and (craves ?a ?c) (located_in ?b ?d) (not (craves ?a ?b)) (not (located_in ?b ?e)))
  )

  (:action succumb_to_pleasure
    :parameters (?a - pain ?b - pleasure ?c - food ?d - object ?e - object)
    :precondition (and (fears ?a ?b) (is_pain ?a) (is_pleasure ?b) (craves ?b ?c) (is_food ?c) (in_harmony_with ?b ?d) (orbits ?d ?e))
    :effect (and (craves ?a ?c) (in_harmony_with ?b ?e) (not (fears ?a ?b)) (not (in_harmony_with ?b ?d)))
  )

  (:action drink_from_objects
    :parameters (?a - object ?b - object ?c - object ?d - object ?e - object ?f - object ?g - object)
    :precondition (and (located_in ?a ?c) (attacks ?d ?c) (attacks ?e ?d) (located_in ?b ?f) (attacks ?f ?g) (not (= ?a ?b)))
    :effect (and (located_in ?a ?d) (located_in ?b ?g) (not (located_in ?a ?c)) (not (located_in ?b ?f)))
  )

)