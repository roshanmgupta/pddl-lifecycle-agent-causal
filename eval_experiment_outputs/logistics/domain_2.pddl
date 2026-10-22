(define (domain logistics)
  (:requirements :strips :typing)

  (:types
    city location package vehicle - object
    airplane truck - vehicle
    airport - location
  )

  (:predicates
    (at ?obj - object ?loc - location)
    (in ?pkg - package ?veh - vehicle)
  )

  (:action load-truck
    :parameters (?pkg - package ?t - truck ?loc - location)
    :precondition (and (at ?pkg ?loc) (at ?t ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?t))
  )

)