(define (domain pipeline_distribution)
  (:requirements :strips :typing)

  (:types
    area batch_atom pipe product - object
  )

  (:predicates
    (normal ?p - pipe)
    (being_push_updated ?p - pipe)
    (being_pop_updated ?p - pipe)
    (first_in ?b - batch_atom ?p - pipe)
    (last_in ?b - batch_atom ?p - pipe)
    (connect ?a1 - area ?a2 - area ?p - pipe)
    (on ?b - batch_atom ?a - area)
    (product_of ?b - batch_atom ?p - product)
    (may_interface ?p1 - product ?p2 - product)
    (follows ?b1 - batch_atom ?b2 - batch_atom)
    (unitary ?p - pipe)
  )

  (:action push_start
    :parameters (?A - pipe ?B - batch_atom ?C - area ?D - area ?E - batch_atom ?F - product ?G - product)
    :precondition (and (normal ?A) (first_in ?E ?A) (connect ?C ?D ?A) (on ?B ?C) (not (unitary ?A)) (product_of ?B ?F) (product_of ?E ?G) (may_interface ?F ?G))
    :effect (and (being_push_updated ?A) (first_in ?B ?A) (follows ?E ?B) (not (normal ?A)) (not (first_in ?E ?A)) (not (on ?B ?C)))
  )

  (:action push_end
    :parameters (?A - pipe ?B - area ?C - area ?D - batch_atom ?E - batch_atom)
    :precondition (and (being_push_updated ?A) (last_in ?D ?A) (connect ?B ?C ?A) (not (unitary ?A)) (follows ?D ?E))
    :effect (and (normal ?A) (last_in ?E ?A) (on ?D ?C) (not (being_push_updated ?A)) (not (follows ?D ?E)) (not (last_in ?D ?A)))
  )

  (:action pop_start
    :parameters (?A - pipe ?B - batch_atom ?C - area ?D - area ?E - batch_atom ?F - product ?G - product)
    :precondition (and (normal ?A) (last_in ?E ?A) (connect ?C ?D ?A) (on ?B ?D) (not (unitary ?A)) (product_of ?B ?F) (product_of ?E ?G) (may_interface ?F ?G))
    :effect (and (being_pop_updated ?A) (last_in ?B ?A) (follows ?B ?E) (not (normal ?A)) (not (last_in ?E ?A)) (not (on ?B ?D)))
  )

  (:action pop_end
    :parameters (?A - pipe ?B - area ?C - area ?D - batch_atom ?E - batch_atom)
    :precondition (and (being_pop_updated ?A) (first_in ?D ?A) (connect ?B ?C ?A) (not (unitary ?A)) (follows ?E ?D))
    :effect (and (normal ?A) (first_in ?E ?A) (on ?D ?B) (not (being_pop_updated ?A)) (not (follows ?E ?D)) (not (first_in ?D ?A)))
  )

  (:action push_unitary
    :parameters (?A - pipe ?B - batch_atom ?C - area ?D - area ?E - batch_atom ?F - product ?G - product)
    :precondition (and (first_in ?E ?A) (connect ?C ?D ?A) (on ?B ?C) (unitary ?A) (product_of ?B ?F) (product_of ?E ?G) (may_interface ?F ?G))
    :effect (and (first_in ?B ?A) (last_in ?B ?A) (on ?E ?D) (not (first_in ?E ?A)) (not (last_in ?E ?A)) (not (on ?B ?C)))
  )

  (:action pop_unitary
    :parameters (?A - pipe ?B - batch_atom ?C - area ?D - area ?E - batch_atom ?F - product ?G - product)
    :precondition (and (last_in ?E ?A) (connect ?C ?D ?A) (on ?B ?D) (unitary ?A) (product_of ?B ?F) (product_of ?E ?G) (may_interface ?F ?G))
    :effect (and (last_in ?B ?A) (first_in ?B ?A) (on ?E ?C) (not (last_in ?E ?A)) (not (first_in ?E ?A)) (not (on ?B ?D)))
  )

  (:action initialize_pipe
    :parameters (?A - pipe ?B - batch_atom ?C - area ?D - area)
    :precondition (and (connect ?C ?D ?A) (on ?B ?C))
    :effect (and (normal ?A) (first_in ?B ?A) (last_in ?B ?A))
  )

)