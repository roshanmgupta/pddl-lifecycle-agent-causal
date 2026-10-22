(define (domain mystery98)
  (:requirements :strips :typing)

  (:types
    food object pain planet pleasure province - object
  )

  (:predicates
    (craves ?a - pain ?f - food)
    (craves ?p - pleasure ?f - food)
    (fears ?a - pain ?p - pleasure)
    (in_harmony ?p - pleasure ?o - object)
    (eats ?f1 - food ?f2 - food)
    (located_in ?f - food ?p - province)
    (attacks ?p1 - province ?p2 - province)
    (orbits ?p1 - planet ?p2 - planet)
    (is_food ?f - food)
    (is_pleasure ?p - pleasure)
    (is_pain ?a - pain)
    (is_province ?p - province)
    (is_planet ?p - planet)
  )

  (:action overcome
    :parameters (?a - pain ?b - pleasure ?c - food ?d - planet ?e - planet)
    :precondition (and (is_pain ?a) (is_pleasure ?b) (craves ?a ?c) (craves ?b ?c) (is_food ?c) (in_harmony ?b ?e) (is_planet ?e) (orbits ?d ?e) (is_planet ?d))
    :effect (and (fears ?a ?b) (in_harmony ?b ?d) (not (craves ?a ?c)) (not (in_harmony ?b ?e)))
  )

  (:action feast
    :parameters (?a - pleasure ?b - food ?c - food ?d - province ?e - province)
    :precondition (and (craves ?a ?b) (is_food ?b) (is_pleasure ?a) (eats ?b ?c) (is_food ?c) (located_in ?b ?e) (attacks ?d ?e))
    :effect (and (craves ?a ?c) (located_in ?b ?d) (not (craves ?a ?b)) (not (located_in ?b ?e)))
  )

  (:action succumb
    :parameters (?a - pain ?b - pleasure ?c - food ?d - planet ?e - object)
    :precondition (and (fears ?a ?b) (is_pain ?a) (is_pleasure ?b) (craves ?b ?c) (is_food ?c) (in_harmony ?b ?d) (orbits ?d ?e))
    :effect (and (craves ?a ?c) (in_harmony ?b ?e) (not (fears ?a ?b)) (not (in_harmony ?b ?d)))
  )

)