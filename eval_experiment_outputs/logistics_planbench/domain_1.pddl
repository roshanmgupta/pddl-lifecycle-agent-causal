(define (domain logistics_planbench)
  (:requirements :strips :typing)

  (:types
    airplane city location package truck - object
  )

  (:predicates
    (at ?p - package ?l - location)
    (in-truck ?p - package ?t - truck)
    (in-airplane ?p - package ?a - airplane)
    (truck-at ?t - truck ?l - location)
    (airplane-at ?a - airplane ?l - location)
    (location-in-city ?l - location ?c - city)
    (airport ?l - location)
  )

  (:action load-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?p ?l) (truck-at ?t ?l))
    :effect (and (not (at ?p ?l)) (in-truck ?p ?t))
  )

  (:action load-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (at ?p ?l) (airplane-at ?a ?l))
    :effect (and (not (at ?p ?l)) (in-airplane ?p ?a))
  )

  (:action unload-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (in-truck ?p ?t) (truck-at ?t ?l))
    :effect (and (not (in-truck ?p ?t)) (at ?p ?l))
  )

  (:action unload-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (in-airplane ?p ?a) (airplane-at ?a ?l))
    :effect (and (not (in-airplane ?p ?a)) (at ?p ?l))
  )

  (:action drive-truck
    :parameters (?t - truck ?from - location ?to - location ?c - city)
    :precondition (and (truck-at ?t ?from) (location-in-city ?from ?c) (location-in-city ?to ?c))
    :effect (and (not (truck-at ?t ?from)) (truck-at ?t ?to))
  )

  (:action fly-airplane
    :parameters (?a - airplane ?from - location ?to - location)
    :precondition (and (airplane-at ?a ?from) (airport ?from) (airport ?to))
    :effect (and (not (airplane-at ?a ?from)) (airplane-at ?a ?to))
  )

)