(define (domain painting_domain)
  (:requirements :strips :typing)

  (:types
    color robot tile - object
  )

  (:predicates
    (at ?r - robot ?t - tile)
    (has ?r - robot ?c - color)
    (painted ?t - tile ?c - color)
    (clear ?t - tile)
    (up ?t1 - tile ?t2 - tile)
    (down ?t1 - tile ?t2 - tile)
    (left ?t1 - tile ?t2 - tile)
    (right ?t1 - tile ?t2 - tile)
  )

  (:action change_color
    :parameters (?r - robot ?c1 - color ?c2 - color)
    :precondition (has ?r ?c1)
    :effect (and (not (has ?r ?c1)) (has ?r ?c2))
  )

  (:action paint_up
    :parameters (?r - robot ?t1 - tile ?t2 - tile ?c - color)
    :precondition (and (has ?r ?c) (at ?r ?t1) (up ?t2 ?t1) (clear ?t2))
    :effect (and (painted ?t2 ?c) (not (clear ?t2)))
  )

  (:action paint_down
    :parameters (?r - robot ?t1 - tile ?t2 - tile ?c - color)
    :precondition (and (has ?r ?c) (at ?r ?t1) (down ?t2 ?t1) (clear ?t2))
    :effect (and (painted ?t2 ?c) (not (clear ?t2)))
  )

  (:action paint_left
    :parameters (?r - robot ?t1 - tile ?t2 - tile ?c - color)
    :precondition (and (has ?r ?c) (at ?r ?t1) (left ?t2 ?t1) (clear ?t2))
    :effect (and (painted ?t2 ?c) (not (clear ?t2)))
  )

  (:action paint_right
    :parameters (?r - robot ?t1 - tile ?t2 - tile ?c - color)
    :precondition (and (has ?r ?c) (at ?r ?t1) (right ?t2 ?t1) (clear ?t2))
    :effect (and (painted ?t2 ?c) (not (clear ?t2)))
  )

  (:action move_up
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (up ?t2 ?t1) (clear ?t2))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1) (not (clear ?t2)))
  )

  (:action move_down
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (down ?t2 ?t1) (clear ?t2))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1) (not (clear ?t2)))
  )

  (:action move_left
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (left ?t2 ?t1) (clear ?t2))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1) (not (clear ?t2)))
  )

  (:action move_right
    :parameters (?r - robot ?t1 - tile ?t2 - tile)
    :precondition (and (at ?r ?t1) (right ?t2 ?t1) (clear ?t2))
    :effect (and (not (at ?r ?t1)) (at ?r ?t2) (clear ?t1) (not (clear ?t2)))
  )

)