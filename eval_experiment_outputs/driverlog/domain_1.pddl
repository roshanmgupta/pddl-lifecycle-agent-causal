(define (domain driverlog)
  (:requirements :strips :typing)

  (:types
    driver location object truck - object
  )

  (:predicates
    (at ?x - object ?y - location)
    (in ?x - object ?y - truck)
    (empty ?x - truck)
    (driving ?x - driver ?y - truck)
    (linked ?x - location ?y - location)
    (path ?x - location ?y - location)
  )

  (:action load
    :parameters (?a - object ?b - truck ?c - location)
    :precondition (and (at ?a ?c) (at ?b ?c))
    :effect (and (in ?a ?b) (not (at ?a ?c)))
  )

  (:action unload
    :parameters (?a - object ?b - truck ?c - location)
    :precondition (and (in ?a ?b) (at ?b ?c))
    :effect (and (at ?a ?c) (not (in ?a ?b)))
  )

  (:action board
    :parameters (?a - driver ?b - truck ?c - location)
    :precondition (and (at ?a ?c) (at ?b ?c) (empty ?b))
    :effect (and (driving ?a ?b) (not (at ?a ?c)) (not (empty ?b)))
  )

  (:action disembark
    :parameters (?a - driver ?b - truck ?c - location)
    :precondition (and (driving ?a ?b) (at ?b ?c))
    :effect (and (at ?a ?c) (empty ?b) (not (driving ?a ?b)))
  )

  (:action drive
    :parameters (?a - truck ?b - location ?c - location ?d - driver)
    :precondition (and (at ?a ?b) (driving ?d ?a) (linked ?b ?c))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action walk
    :parameters (?a - driver ?b - location ?c - location)
    :precondition (and (at ?a ?b) (path ?b ?c))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

)