(define (domain spanner)
  (:requirements :strips :typing)

  (:types
    locatable - object
    location man nut spanner - locatable
  )

  (:predicates
    (link ?from - location ?to - location)
    (at ?x - locatable ?l - location)
    (loose ?n - nut)
    (useable ?s - spanner)
    (tightened ?n - nut)
  )

  (:action walk
    :parameters (?start - location ?end - location ?m - man)
    :precondition (and (link ?start ?end) (at ?m ?start))
    :effect (and (not (at ?m ?start)) (at ?m ?end))
  )

  (:action pickup_spanner
    :parameters (?l - location ?s - spanner ?m - man)
    :precondition (and (at ?s ?l) (at ?m ?l) (useable ?s))
    :effect (and (not (at ?s ?l)) (not (useable ?s)))
  )

  (:action tighten_nut
    :parameters (?l - location ?s - spanner ?m - man ?n - nut)
    :precondition (and (at ?m ?l) (at ?n ?l) (loose ?n))
    :effect (and (not (loose ?n)) (tightened ?n))
  )

)