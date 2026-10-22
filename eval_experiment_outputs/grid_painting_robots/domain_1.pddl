(define (domain grid_painting_robots)
  (:requirements :strips :typing :negative-preconditions :equality)

  (:types
    color direction robot tile - object
  )

  (:predicates
    (at ?r - robot ?t - tile)
    (facing ?r - robot ?d - direction)
    (adjacent ?from - tile ?to - tile ?d - direction)
    (opposite ?d1 - direction ?d2 - direction)
    (painted ?t - tile)
    (painted_with ?t - tile ?c - color)
    (active_color ?r - robot ?c - color)
    (has_sprayer ?r - robot ?c - color)
    (clear ?t - tile)
    (paint_station ?t - tile)
  )

  (:action move
    :parameters (?r - robot ?from - tile ?to - tile ?d - direction)
    :precondition (and (at ?r ?from) (facing ?r ?d) (adjacent ?from ?to ?d) (clear ?to) (not (painted ?to)))
    :effect (and (not (at ?r ?from)) (at ?r ?to) (clear ?from) (not (clear ?to)))
  )

  (:action turn
    :parameters (?r - robot ?old - direction ?new - direction)
    :precondition (and (facing ?r ?old) (not (= ?old ?new)))
    :effect (and (not (facing ?r ?old)) (facing ?r ?new))
  )

  (:action spray_front
    :parameters (?r - robot ?from - tile ?target - tile ?c - color ?d - direction)
    :precondition (and (at ?r ?from) (facing ?r ?d) (active_color ?r ?c) (adjacent ?from ?target ?d) (clear ?target) (not (painted ?target)))
    :effect (and (painted ?target) (painted_with ?target ?c))
  )

  (:action spray_behind
    :parameters (?r - robot ?from - tile ?target - tile ?c - color ?d_front - direction ?d_behind - direction)
    :precondition (and (at ?r ?from) (facing ?r ?d_front) (active_color ?r ?c) (adjacent ?from ?target ?d_behind) (opposite ?d_front ?d_behind) (clear ?target) (not (painted ?target)))
    :effect (and (painted ?target) (painted_with ?target ?c))
  )

  (:action switch_color
    :parameters (?r - robot ?t - tile ?old - color ?new - color)
    :precondition (and (at ?r ?t) (paint_station ?t) (active_color ?r ?old) (has_sprayer ?r ?new) (not (= ?old ?new)))
    :effect (and (not (active_color ?r ?old)) (active_color ?r ?new))
  )

)