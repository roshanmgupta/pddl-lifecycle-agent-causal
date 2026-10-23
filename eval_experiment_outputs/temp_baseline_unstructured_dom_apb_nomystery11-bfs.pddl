(define (domain nomystery11-bfs)
  (:requirements :strips :typing)
  (:types
    location package truck locatable fuellevel - object
  )
  (:predicates
    (at ?p - locatable ?l - location)
    (in ?p - package ?t - truck)
    (connected ?l1 - location ?l2 - location)
    (fuel-cost ?f1 - fuellevel ?l - location ?f2 - fuellevel)
    (has-fuel ?t - truck ?f - fuellevel)
  )
  (:action load-package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?p ?l) (at ?t ?l))
    :effect (and (in ?p ?t) (not (at ?p ?l)))
  )
  (:action unload-package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (in ?p ?t) (at ?t ?l))
    :effect (and (at ?p ?l) (not (in ?p ?t)))
  )
  (:action drive
    :parameters (?t - truck ?l1 - location ?l2 - location ?f1 - fuellevel ?f2 - fuellevel)
    :precondition (and (connected ?l1 ?l2) (fuel-cost ?f1 ?l1 ?f2) (has-fuel ?t ?f1) (not (= ?f1 ?f2)))
    :effect (and (at ?t ?l2) (not (at ?t ?l1)) (has-fuel ?t ?f2))
  )
)