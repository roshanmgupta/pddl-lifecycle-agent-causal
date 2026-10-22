(define (domain logistics00)
  (:requirements :strips :typing)
  (:types
    package truck airplane location airport city - object
  )
  (:predicates
    (is-package ?p - package)
    (is-truck ?t - truck)
    (is-airplane ?a - airplane)
    (is-location ?l - location)
    (is-airport ?a - airport)
    (is-city ?c - city)
    (at ?o - object ?l - location)
    (in ?p - package ?v - (or truck airplane))
    (in-city ?l - location ?c - city)
  )
  (:action load-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (is-package ?p) (is-truck ?t) (is-location ?l) (at ?t ?l) (at ?p ?l))
    :effect (and (in ?p ?t) (not (at ?p ?l)))
  )
  (:action load-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (is-package ?p) (is-airplane ?a) (is-location ?l) (at ?p ?l) (at ?a ?l))
    :effect (and (in ?p ?a) (not (at ?p ?l)))
  )
  (:action unload-truck
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (is-package ?p) (is-truck ?t) (is-location ?l) (at ?t ?l) (in ?p ?t))
    :effect (and (at ?p ?l) (not (in ?p ?t)))
  )
  (:action unload-airplane
    :parameters (?p - package ?a - airplane ?l - location)
    :precondition (and (is-package ?p) (is-airplane ?a) (is-location ?l) (at ?a ?l) (in ?p ?a))
    :effect (and (at ?p ?l) (not (in ?p ?a)))
  )
  (:action drive-truck
    :parameters (?t - truck ?from - location ?to - location ?c - city)
    :precondition (and (is-truck ?t) (is-location ?from) (is-location ?to) (is-city ?c) (at ?t ?from) (in-city ?from ?c) (in-city ?to ?c))
    :effect (and (at ?t ?to) (not (at ?t ?from)))
  )
  (:action fly-airplane
    :parameters (?a - airplane ?from - airport ?to - airport)
    :precondition (and (is-airplane ?a) (is-airport ?from) (is-airport ?to) (at ?a ?from))
    :effect (and (at ?a ?to) (not (at ?a ?from)))
  )
)