(define (domain transportation_logistics)
  (:requirements :strips :typing)

  (:types
    driver package truck - entity
    entity human location vehicle - object
  )

  (:predicates
    (at ?e - entity ?l - location)
    (path_connected ?from - location ?to - location)
    (road_connected ?from - location ?to - location)
    (boarded ?d - driver ?t - truck)
    (loaded ?p - package ?t - truck)
  )

  (:action walk
    :parameters (?d - driver ?from - location ?to - location)
    :precondition (and (at ?d ?from) (path_connected ?from ?to))
    :effect (and (not (at ?d ?from)) (at ?d ?to))
  )

  (:action board_truck
    :parameters (?d - driver ?t - truck ?l - location)
    :precondition (and (at ?d ?l) (at ?t ?l))
    :effect (and (boarded ?d ?t) (not (at ?d ?l)))
  )

  (:action drive_truck
    :parameters (?d - driver ?t - truck ?from - location ?to - location)
    :precondition (and (boarded ?d ?t) (at ?t ?from) (road_connected ?from ?to))
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action load_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?p ?l) (at ?t ?l))
    :effect (and (loaded ?p ?t) (not (at ?p ?l)))
  )

  (:action unload_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (loaded ?p ?t) (at ?t ?l))
    :effect (and (at ?p ?l) (not (loaded ?p ?t)))
  )

)