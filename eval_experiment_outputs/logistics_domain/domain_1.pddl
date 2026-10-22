(define (domain logistics_domain)
  (:requirements :strips :typing)

  (:types
    airplane location package truck - object
    airport - location
  )

  (:predicates
    (at_truck ?t - truck ?l - location)
    (at_airplane ?p - airplane ?a - airport)
    (at_pkg ?pkg - package ?l - location)
    (in_truck ?pkg - package ?t - truck)
    (in_airplane ?pkg - package ?p - airplane)
    (same_city ?l1 - location ?l2 - location)
  )

  (:action truck_move
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at_truck ?t ?from) (same_city ?from ?to))
    :effect (and (not (at_truck ?t ?from)) (at_truck ?t ?to))
  )

  (:action airplane_fly
    :parameters (?p - airplane ?from - airport ?to - airport)
    :precondition (at_airplane ?p ?from)
    :effect (and (not (at_airplane ?p ?from)) (at_airplane ?p ?to))
  )

  (:action load_truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (at_pkg ?pkg ?loc) (at_truck ?t ?loc))
    :effect (and (not (at_pkg ?pkg ?loc)) (in_truck ?pkg ?t))
  )

  (:action unload_truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (in_truck ?pkg ?t) (at_truck ?t ?loc))
    :effect (and (not (in_truck ?pkg ?t)) (at_pkg ?pkg ?loc))
  )

  (:action load_airplane
    :parameters (?pkg - package ?p - airplane ?apt - airport)
    :precondition (and (at_pkg ?pkg ?apt) (at_airplane ?p ?apt))
    :effect (and (not (at_pkg ?pkg ?apt)) (in_airplane ?pkg ?p))
  )

  (:action unload_airplane
    :parameters (?pkg - package ?p - airplane ?apt - airport)
    :precondition (and (in_airplane ?pkg ?p) (at_airplane ?p ?apt))
    :effect (and (not (in_airplane ?pkg ?p)) (at_pkg ?pkg ?apt))
  )

)