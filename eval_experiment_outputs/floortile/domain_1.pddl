(define (domain floortile)
  (:requirements :strips :typing)

  (:types
    color robot tile - object
  )

  (:predicates
    (has ?r - robot ?c - color)
    (at ?r - robot ?t - tile)
    (clear ?t - tile)
    (painted ?t - tile ?c - color)
    (available ?c - color)
    (up ?t1 - tile ?t2 - tile)
    (down ?t1 - tile ?t2 - tile)
    (right-of ?t1 - tile ?t2 - tile)
    (left-of ?t1 - tile ?t2 - tile)
  )

  (:action change_color
    :parameters (?a - robot ?b - color ?c - color)
    :precondition (and (has ?a ?b) (available ?c))
    :effect (and (not (has ?a ?b)) (has ?a ?c))
  )

  (:action paint_up
    :parameters (?a - robot ?b - tile ?c - tile ?d - color)
    :precondition (and (has ?a ?d) (at ?a ?c) (up ?b ?c) (clear ?b))
    :effect (and (painted ?b ?d) (not (clear ?b)))
  )

  (:action paint_down
    :parameters (?a - robot ?b - tile ?c - tile ?d - color)
    :precondition (and (has ?a ?d) (at ?a ?c) (down ?b ?c) (clear ?b))
    :effect (and (painted ?b ?d) (not (clear ?b)))
  )

  (:action move_up
    :parameters (?a - robot ?b - tile ?c - tile)
    :precondition (and (at ?a ?b) (up ?c ?b) (clear ?c))
    :effect (and (not (at ?a ?b)) (at ?a ?c) (clear ?b) (not (clear ?c)))
  )

  (:action move_down
    :parameters (?a - robot ?b - tile ?c - tile)
    :precondition (and (at ?a ?b) (down ?c ?b) (clear ?c))
    :effect (and (not (at ?a ?b)) (at ?a ?c) (clear ?b) (not (clear ?c)))
  )

  (:action move_right
    :parameters (?a - robot ?b - tile ?c - tile)
    :precondition (and (at ?a ?b) (right-of ?c ?b) (clear ?c))
    :effect (and (not (at ?a ?b)) (at ?a ?c) (clear ?b) (not (clear ?c)))
  )

  (:action move_left
    :parameters (?a - robot ?b - tile ?c - tile)
    :precondition (and (at ?a ?b) (left-of ?c ?b) (clear ?c))
    :effect (and (not (at ?a ?b)) (at ?a ?c) (clear ?b) (not (clear ?c)))
  )

)