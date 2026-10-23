(define (domain nomystery11-bfs)
  (:requirements :strips :typing)

  (:types
    fuellevel locatable location - object
    package truck - locatable
  )

  (:predicates
    (at ?x - locatable ?y - location)
    (in ?p - locatable ?t - object)
    (connected ?l1 - location ?l2 - location)
    (fuel-cost ?f1 - fuellevel ?l - location ?f2 - fuellevel)
    (has-fuel ?t - truck ?f_start - fuellevel)
  )

  (:action load_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (at ?p ?l))
    :effect (and (in ?p ?t) (not (at ?p ?l)))
  )

  (:action unload_package
    :parameters (?p - package ?t - truck ?l - location)
    :precondition (and (at ?t ?l) (in ?p ?t))
    :effect (and (at ?p ?l) (not (in ?p ?t)))
  )

  (:action drive_truck
    :parameters (?t - truck ?from - location ?to - location ?f_cost - fuellevel ?f_start - fuellevel ?f_end - fuellevel)
    :precondition (and (connected ?from ?to) (fuel-cost ?f_cost ?from ?f_end) (at ?t ?from) (not (at ?t ?to)) (not (in ?t ?from)))
    :effect (and (at ?t ?to) (not (at ?t ?from)) (not (has-fuel ?t ?f_start)) (has-fuel ?t ?f_end))
  )

)