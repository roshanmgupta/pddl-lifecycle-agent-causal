(define (domain logistics)
  (:requirements :strips :typing)

  (:types
    airplane city location obj truck - object
    airport - location
  )

  (:predicates
    (is_at ?x - obj ?y - location)
    (is_in ?x - obj ?y - (either truck airplane))
    (is_at_vehicle ?x - (either truck airplane) ?y - location)
    (is_in_city ?x - location ?y - city)
    (is_airport ?x - location)
  )

  (:action load_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (is_at ?a ?c) (is_at_vehicle ?b ?c))
    :effect (and (is_in ?a ?b) (not (is_at ?a ?c)))
  )

  (:action load_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (is_at ?a ?c) (is_at_vehicle ?b ?c))
    :effect (and (is_in ?a ?b) (not (is_at ?a ?c)))
  )

  (:action unload_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (is_in ?a ?b) (is_at_vehicle ?b ?c))
    :effect (and (is_at ?a ?c) (not (is_in ?a ?b)))
  )

  (:action unload_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (is_in ?a ?b) (is_at_vehicle ?b ?c))
    :effect (and (is_at ?a ?c) (not (is_in ?a ?b)))
  )

  (:action drive_truck
    :parameters (?a - truck ?b - location ?c - location ?d - city)
    :precondition (and (is_at_vehicle ?a ?b) (is_in_city ?b ?d) (is_in_city ?c ?d))
    :effect (and (is_at_vehicle ?a ?c) (not (is_at_vehicle ?a ?b)))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?b - airport ?c - airport)
    :precondition (and (is_at_vehicle ?a ?b) (is_airport ?b) (is_airport ?c))
    :effect (and (is_at_vehicle ?a ?c) (not (is_at_vehicle ?a ?b)))
  )

)