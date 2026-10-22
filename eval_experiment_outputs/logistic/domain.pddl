(define (domain logistics)
  (:requirements :strips :typing)

  (:types
    airplane airport location package truck - object
  )

  (:predicates
    (at ?obj - object ?l - location)
    (at-airport ?obj - object ?ap - airport)
    (in ?pkg - package ?c - object)
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (at ?t ?from)
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action fly
    :parameters (?p - airplane ?from - airport ?to - airport)
    :precondition (at-airport ?p ?from)
    :effect (and (not (at-airport ?p ?from)) (at-airport ?p ?to))
  )

  (:action load-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (at ?pkg ?loc) (at ?t ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?t))
  )

  (:action unload-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (in ?pkg ?t) (at ?t ?loc))
    :effect (and (not (in ?pkg ?t)) (at ?pkg ?loc))
  )

  (:action load-airplane
    :parameters (?pkg - package ?p - airplane ?ap - airport)
    :precondition (and (at-airport ?pkg ?ap) (at-airport ?p ?ap))
    :effect (and (not (at-airport ?pkg ?ap)) (in ?pkg ?p))
  )

  (:action unload-airplane
    :parameters (?pkg - package ?p - airplane ?ap - airport)
    :precondition (and (in ?pkg ?p) (at-airport ?p ?ap))
    :effect (and (not (in ?pkg ?p)) (at-airport ?pkg ?ap))
  )

)