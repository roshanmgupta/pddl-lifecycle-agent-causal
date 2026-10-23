(define (domain logistics)
  (:requirements :strips :typing)

  (:types
    airplane city location obj truck - object
    airport - airplane
  )

  (:predicates
    (at ?b - object ?loc - object)
    (in ?x - obj ?b - object)
    (in-city ?loc - location ?c - city)
    (at-airport ?a - airplane ?loc - airport)
  )

  (:action load_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (at ?a ?c) (at ?b ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action load_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (at ?a ?c) (at ?b ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action unload_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (in ?a ?b) (at ?b ?c))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action unload_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (in ?a ?b) (at ?b ?c))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action drive_truck
    :parameters (?a - truck ?b - location ?c - location ?d - city)
    :precondition (and (at ?a ?b) (in-city ?b ?d) (in-city ?c ?d))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?b - airport ?c - airport)
    :precondition (at ?a ?b)
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

)