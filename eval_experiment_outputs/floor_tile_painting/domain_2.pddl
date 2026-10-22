(define (domain floor_tile_painting)
  (:requirements :strips :typing)

  (:types
    color robot tile - object
  )

  (:predicates
    (at ?r - robot ?t - tile)
    (has_color ?r - robot ?c - color)
    (clear ?t - tile)
    (painted ?t - tile ?c - color)
    (up_of ?t1 - tile ?t2 - tile)
    (down_of ?t1 - tile ?t2 - tile)
    (left_of ?t1 - tile ?t2 - tile)
    (right_of ?t1 - tile ?t2 - tile)
  )

  (:action change_color
    :parameters (?r - robot ?c_old - color ?c_new - color)
    :precondition (has_color ?r ?c_old)
    :effect (and (not (has_color ?r ?c_old)) (has_color ?r ?c_new))
  )

  (:action paint_up
    :parameters (?r - robot ?t - tile ?t_up - tile ?c - color)
    :precondition (and (at ?r ?t) (has_color ?r ?c) (up_of ?t ?t_up) (clear ?t_up))
    :effect (and (not (clear ?t_up)) (painted ?t_up ?c))
  )

  (:action paint_down
    :parameters (?r - robot ?t - tile ?t_down - tile ?c - color)
    :precondition (and (at ?r ?t) (has_color ?r ?c) (down_of ?t ?t_down) (clear ?t_down))
    :effect (and (not (clear ?t_down)) (painted ?t_down ?c))
  )

  (:action up
    :parameters (?r - robot ?t - tile ?t_up - tile)
    :precondition (and (at ?r ?t) (up_of ?t ?t_up) (clear ?t_up))
    :effect (and (not (at ?r ?t)) (not (clear ?t_up)) (at ?r ?t_up) (clear ?t))
  )

  (:action down
    :parameters (?r - robot ?t - tile ?t_down - tile)
    :precondition (and (at ?r ?t) (down_of ?t ?t_down) (clear ?t_down))
    :effect (and (not (at ?r ?t)) (not (clear ?t_down)) (at ?r ?t_down) (clear ?t))
  )

  (:action right
    :parameters (?r - robot ?t - tile ?t_right - tile)
    :precondition (and (at ?r ?t) (right_of ?t ?t_right) (clear ?t_right))
    :effect (and (not (at ?r ?t)) (not (clear ?t_right)) (at ?r ?t_right) (clear ?t))
  )

  (:action left
    :parameters (?r - robot ?t - tile ?t_left - tile)
    :precondition (and (at ?r ?t) (left_of ?t ?t_left) (clear ?t_left))
    :effect (and (not (at ?r ?t)) (not (clear ?t_left)) (at ?r ?t_left) (clear ?t))
  )

)