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
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (is_package ?p) (is_truck ?t) (is_location ?l) (at ?t ?l) (at ?p ?l))
    :effect (and (in ?p ?t) (not (at ?p ?l)))
  )

  (:action load_airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (is_package ?p) (is_airplane ?a) (is_location ?l) (at ?a ?l) (at ?p ?l))
    :effect (and (in ?p ?a) (not (at ?p ?l)))
  )

  (:action unload_truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (is_package ?p) (is_truck ?t) (is_location ?l) (at ?t ?l) (in ?p ?t))
    :effect (and (at ?p ?l) (not (in ?p ?t)))
  )

  (:action unload_airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (is_package ?p) (is_airplane ?a) (is_location ?l) (at ?a ?l) (in ?p ?a))
    :effect (and (at ?p ?l) (not (in ?p ?a)))
  )

  (:action drive_truck
    :parameters (?t - truck ?from - location ?to - location ?c - city)
    :precondition (and (is_truck ?t) (is_location ?from) (is_location ?to) (is_city ?c) (at ?t ?from) (in_city ?from ?c) (in_city ?to ?c))
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?from - location ?to - location)
    :precondition (and (is_airplane ?a) (is_location ?from) (is_location ?to) (is_airport ?from) (is_airport ?to) (at ?a ?from))
    :effect (and (at ?a ?to) (not (at ?a ?from)))
  )

)