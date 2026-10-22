(define (domain robotic_painting)
  (:requirements :strips :typing)

  (:types
    color paint_station robot tile - object
  )

  (:predicates
    (at ?r - robot ?t - tile)
    (adjacent ?t1 - tile ?t2 - tile)
    (painted ?t - tile ?c - color)
    (unpainted ?t - tile)
    (current_color ?r - robot ?c - color)
    (at_paint_station ?r - robot ?ps - paint_station)
  )

  (:action move
    :parameters (?r - robot ?from - tile ?to - tile)
    :precondition (and (at ?r ?from) (adjacent ?from ?to) (unpainted ?to))
    :effect (and (not (at ?r ?from)) (at ?r ?to))
  )

  (:action paint
    :parameters (?r - robot ?t - tile ?c - color)
    :precondition (and (at ?r ?t) (current_color ?r ?c) (unpainted ?t))
    :effect (and (not (unpainted ?t)) (painted ?t ?c))
  )

  (:action change_color
    :parameters (?r - robot ?ps - paint_station ?new_color - color ?old_color - color)
    :precondition (and (at_paint_station ?r ?ps) (current_color ?r ?old_color))
    :effect (and (not (current_color ?r ?old_color)) (current_color ?r ?new_color))
  )

)