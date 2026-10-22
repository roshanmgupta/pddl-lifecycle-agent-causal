(define (domain logistics_domain)
  (:requirements :strips :typing)

  (:types
    airplane city location movable obj truck - object
    airport - location
  )

  (:predicates
    (is_obj ?o - obj)
    (is_truck ?t - truck)
    (is_airplane ?a - airplane)
    (is_location ?l - location)
    (is_airport ?a - airport)
    (is_city ?c - city)
    (at ?m - movable ?l - location)
    (in ?o - obj ?v - truck)
    (in ?o - obj ?v - airplane)
    (in_city ?l - location ?c - city)
  )

  (:action load_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (is_obj ?a) (is_truck ?b) (is_location ?c) (at ?b ?c) (at ?a ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action load_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (is_obj ?a) (is_airplane ?b) (is_location ?c) (at ?b ?c) (at ?a ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action unload_truck
    :parameters (?a - obj ?b - truck ?c - location)
    :precondition (and (is_obj ?a) (is_truck ?b) (is_location ?c) (at ?b ?c) (in ?a ?b))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action unload_airplane
    :parameters (?a - obj ?b - airplane ?c - location)
    :precondition (and (is_obj ?a) (is_airplane ?b) (is_location ?c) (at ?b ?c) (in ?a ?b))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action drive_truck
    :parameters (?a - truck ?b - location ?c - location ?d - city)
    :precondition (and (is_truck ?a) (is_location ?b) (is_location ?c) (is_city ?d) (at ?a ?b) (in_city ?b ?d) (in_city ?c ?d))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?b - airport ?c - airport)
    :precondition (and (is_airplane ?a) (is_airport ?b) (is_airport ?c) (at ?a ?b))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

)