(define (domain block_world)
  (:requirements pick_up put_down)

  (:types
    block table - location
    location - object
    robot - agent
  )

  (:predicates
    (at ?r - robot ?l - location)
    (on ?x - block ?y - location)
    (clear ?l - location)
    (holding ?r - robot ?o - block)
    (handempty ?r - robot)
  )

  (:action pick_up
    :parameters (?l - location ?o - block ?r - robot)
    :precondition (and (at ?r ?l) (on ?o ?l) (clear ?o) (handempty ?r))
    :effect (and (holding ?r ?o) (not (on ?o ?l)) (not (clear ?o)) (not (handempty ?r)) (clear ?l))
  )

  (:action put_down
    :parameters (?l - location ?o - block ?r - robot)
    :precondition (and (holding ?r ?o) (clear ?l))
    :effect (and (not (holding ?r ?o)) (on ?o ?l) (not (clear ?l)) (handempty ?r) (clear ?o))
  )

)