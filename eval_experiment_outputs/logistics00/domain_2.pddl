(define (domain logistics00)
  (:requirements :strips :typing)

  (:types
    airplane city location package truck - object
    airport - location
  )

  (:predicates
    (is_package ?p - package)
    (is_truck ?t - truck)
    (is_airplane ?a - airplane)
    (is_location ?l - location)
    (is_airport ?a - airport)
    (is_city ?c - city)
    (at ?o - object ?l - location)
    (in ?p - package ?v - object)
    (in_city ?l - location ?c - city)
  )

  (:action load_truck
    :parameters (?a - package ?b - truck ?c - location)
    :precondition (and (is_package ?a) (is_truck ?b) (is_location ?c) (at ?b ?c) (at ?a ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action load_airplane
    :parameters (?a - package ?b - airplane ?c - location)
    :precondition (and (is_package ?a) (is_airplane ?b) (is_location ?c) (at ?b ?c) (at ?a ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action unload_truck
    :parameters (?a - package ?b - truck ?c - location)
    :precondition (and (is_package ?a) (is_truck ?b) (is_location ?c) (at ?b ?c) (in ?a ?b))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action unload_airplane
    :parameters (?a - package ?b - airplane ?c - location)
    :precondition (and (is_package ?a) (is_airplane ?b) (is_location ?c) (at ?b ?c) (in ?a ?b))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action drive_truck
    :parameters (?a - truck ?b - location ?c - location ?d - city)
    :precondition (and (is_truck ?a) (is_location ?b) (is_location ?c) (is_city ?d) (at ?a ?b) (in_city ?b ?d) (in_city ?c ?d))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?b - airport ?c - airport)
    :precondition (and (is_airplane ?a) (is_airport ?b) (is_airport ?c))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action reposition_airplane
    :parameters (?a - airplane ?b - airport ?c - airport)
    :precondition (and (is_airplane ?a) (is_airport ?b) (is_airport ?c) (at ?a ?b))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

)