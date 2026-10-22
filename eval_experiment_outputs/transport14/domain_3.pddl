(define (domain transport14)
  (:requirements :strips :typing)

  (:types
    capacity-number locatable location - object
    package vehicle - locatable
  )

  (:predicates
    (at ?x - locatable ?y - location)
    (road ?x - location ?y - location)
    (capacity-predecessor ?x - capacity-number ?y - capacity-number)
    (capacity ?x - vehicle ?y - capacity-number)
    (in ?x - package ?y - vehicle)
  )

  (:action drive
    :parameters (?a - vehicle ?b - location ?c - location)
    :precondition (and (at ?a ?b) (road ?b ?c))
    :effect (and (not (at ?a ?b)) (at ?a ?c))
  )

  (:action pick-up
    :parameters (?a - vehicle ?b - location ?c - package ?d - capacity-number ?e - capacity-number)
    :precondition (and (at ?a ?b) (at ?c ?b) (capacity-predecessor ?d ?e) (capacity ?a ?e))
    :effect (and (not (at ?c ?b)) (not (capacity ?a ?e)) (in ?c ?a) (capacity ?a ?d))
  )

  (:action drop
    :parameters (?a - vehicle ?b - location ?c - package ?d - capacity-number ?e - capacity-number)
    :precondition (and (at ?a ?b) (in ?c ?a) (capacity-predecessor ?d ?e) (capacity ?a ?d))
    :effect (and (not (in ?c ?a)) (not (capacity ?a ?d)) (at ?c ?b) (capacity ?a ?e))
  )

)