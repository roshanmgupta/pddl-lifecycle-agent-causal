(define (domain regional_courier)
  (:requirements :strips :typing)

  (:types
    driver location package truck - object
  )

  (:predicates
    (at ?x - object ?l - location)
    (in ?x - object ?t - truck)
    (has_driver ?t - truck)
    (footpath ?l1 - location ?l2 - location)
    (road ?l1 - location ?l2 - location)
    (certified ?d - driver)
    (active ?d - driver)
  )

  (:action walk_driver
    :parameters (?d - driver ?from - location ?to - location)
    :precondition (and (at ?d ?from) (footpath ?from ?to))
    :effect (and (not (at ?d ?from)) (at ?d ?to))
  )

  (:action board_truck
    :parameters (?d - driver ?t - truck ?l - location)
    :precondition (and (at ?d ?l) (at ?t ?l) (not (has_driver ?t)))
    :effect (and (not (at ?d ?l)) (in ?d ?t) (has_driver ?t))
  )

  (:action disembark_truck
    :parameters (?d - driver ?t - truck ?l - location)
    :precondition (and (in ?d ?t) (at ?t ?l))
    :effect (and (not (in ?d ?t)) (not (has_driver ?t)) (at ?d ?l))
  )

  (:action load_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?p ?l) (at ?t ?l) (has_driver ?t))
    :effect (and (not (at ?p ?l)) (in ?p ?t))
  )

  (:action unload_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (in ?p ?t) (at ?t ?l) (has_driver ?t))
    :effect (and (not (in ?p ?t)) (at ?p ?l))
  )

  (:action drive_truck
    :parameters (?t - truck ?d - driver ?from - location ?to - location)
    :precondition (and (at ?t ?from) (in ?d ?t) (road ?from ?to) (certified ?d) (active ?d))
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

)