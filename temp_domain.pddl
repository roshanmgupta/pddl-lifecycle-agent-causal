(define (domain depots)
  (:requirements :strips :typing)

  (:types
    truck - vehicle
    crate - object
    pallet - platform
    location - place
  )

  (:predicates
    (at?c - crate?l - location)
    (at?t - truck?l - location)
    (on?c - crate?p - pallet)
    (on?c - crate?t - truck)
    (in?c - crate?t - truck)
    (empty?p - pallet)
    (empty?t - truck)
    (connected?l1 - location?l2 - location)
  )

  (:action load_truck
    :parameters (?c - crate ?t - truck ?l - location)
    :precondition (and (at?c?l) (at?t?l) (empty?t))
    :effect (and (in?c?t) (not (at?c?l)) (not (empty?t)))
  )

  (:action unload_truck
    :parameters (?c - crate ?t - truck ?l - location)
    :precondition (and (in?c?t) (at?t?l))
    :effect (and (at?c?l) (not (in?c?t)) (empty?t))
  )

  (:action move_truck
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at?t?from) (connected?from?to))
    :effect (and (at?t?to) (not (at?t?from)))
  )

  (:action stack_on_pallet
    :parameters (?c - crate ?p - pallet ?l - location)
    :precondition (and (at?c?l) (at?p?l) (empty?p))
    :effect (and (on?c?p) (not (at?c?l)) (not (empty?p)))
  )

)