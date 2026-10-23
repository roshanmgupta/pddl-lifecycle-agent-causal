(define (domain floortile)
  (:requirements :strips)
  (:predicates
    (at ?r - robot ?t - tile)
    (has ?r - robot ?c - color)
    (clear ?t - tile)
    (painted ?t - tile ?c - color)
    (available ?c - color)
    (up ?t1 - tile ?t2 - tile)
    (down ?t1 - tile ?t2 - tile)
    (right ?t1 - tile ?t2 - tile)
    (left ?t1 - tile ?t2 - tile)
  )
  
  (:action change-color
    :parameters (?r - robot ?c1 - color ?c2 - color)
    :precondition (and (has ?r ?c1) (available ?c2))
    :effect (and (not (has ?r ?c1)) (has ?r ?c2))
  )

  (:action paint
    :parameters (?r - robot ?t1 - tile ?c - color ?t2 - tile)
    :precondition (and (has ?r ?c) (at ?r ?t2) (clear ?t1) (up ?t1 ?t2))
    :effect (and (not (clear ?t1)) (painted ?t1 ?c))
  )

  (:action paint
    :parameters (?r - robot ?t1 - tile ?c - color ?t2 - tile)
    :precondition (and (has ?r ?c) (at ?r ?t2) (clear ?t1) (down ?t1 ?t2))
    :effect (and (not (clear ?t1)) (painted ?t1 ?c))
  )

  (:action move
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (clear ?t2) (up ?t2 ?t1))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1))
  )

  (:action move
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (clear ?t2) (down ?t2 ?t1))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1))
  )

  (:action move
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (clear ?t2) (right ?t2 ?t1))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1))
  )

  (:action move
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (clear ?t2) (left ?t2 ?t1))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1))
  )
)