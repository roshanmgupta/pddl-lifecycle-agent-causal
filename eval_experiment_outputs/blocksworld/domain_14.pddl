(define (domain blocksworld)
  (:requirements :strips :typing :equality :negative-preconditions)

  (:types
    block city location physical_object - object
    package vehicle - physical_object
    airplane truck - vehicle
  )

  (:predicates
    (at ?obj - physical_object ?loc - location)
    (inside ?pkg - package ?veh - vehicle)
    (in-city ?loc - location ?city - city)
    (airport ?loc - location)
    (on ?x - block ?y - block)
    (ontable ?x - block)
    (clear ?x - block)
    (handempty)
    (holding ?x - block)
  )

  (:action move_truck
    :parameters (?t - truck ?from - location ?to - location ?city - city)
    :precondition (and (at ?t ?from) (in-city ?from ?city) (in-city ?to ?city))
    :effect (and (not (at ?t ?from)) (at ?t ?to))
  )

  (:action fly_airplane
    :parameters (?a - airplane ?from - location ?to - location ?from_city - city ?to_city - city)
    :precondition (and (at ?a ?from) (airport ?from) (airport ?to) (in-city ?from ?from_city) (in-city ?to ?to_city) (not (= ?from_city ?to_city)))
    :effect (and (not (at ?a ?from)) (at ?a ?to))
  )

  (:action load_truck
    :parameters (?p - package ?t - truck ?loc - location)
    :precondition (and (at ?p ?loc) (at ?t ?loc))
    :effect (and (not (at ?p ?loc)) (inside ?p ?t))
  )

  (:action unload_truck
    :parameters (?p - package ?t - truck ?loc - location)
    :precondition (and (inside ?p ?t) (at ?t ?loc))
    :effect (and (not (inside ?p ?t)) (at ?p ?loc))
  )

  (:action load_airplane
    :parameters (?p - package ?a - airplane ?apt - location)
    :precondition (and (at ?p ?apt) (at ?a ?apt) (airport ?apt))
    :effect (and (not (at ?p ?apt)) (inside ?p ?a))
  )

  (:action unload_airplane
    :parameters (?p - package ?a - airplane ?apt - location)
    :precondition (and (inside ?p ?a) (at ?a ?apt) (airport ?apt))
    :effect (and (not (inside ?p ?a)) (at ?p ?apt))
  )

  (:action pick_up
    :parameters (?x - block)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x))
  )

  (:action put_down
    :parameters (?x - block)
    :precondition (holding ?x)
    :effect (and (not (holding ?x)) (clear ?x) (ontable ?x) (handempty))
  )

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y))
  )

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (on ?x ?y) (clear ?x) (handempty))
    :effect (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y)))
  )

)