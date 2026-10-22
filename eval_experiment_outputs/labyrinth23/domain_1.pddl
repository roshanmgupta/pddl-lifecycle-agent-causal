(define (domain labyrinth23)
  (:requirements :strips :typing)

  (:types
    card direction gridpos - object
    directionh directionv - direction
  )

  (:predicates
    (robot-at ?c - card)
    (card-at ?c - card ?x - gridpos ?y - gridpos)
    (blocked ?c - card ?d - direction)
    (cards-moving)
    (cards-moving-west)
    (cards-moving-east)
    (cards-moving-north)
    (cards-moving-south)
    (next-moving-card ?c - card)
    (new-headtail-card ?c - card)
    (next-to ?x - gridpos ?y - gridpos)
    (minimum-position ?x - gridpos)
    (maximum-position ?x - gridpos)
    (on-left)
  )

  (:action move-west
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - directionh ?e - card ?f - gridpos ?g - gridpos ?h - direction)
    :precondition (and (= ?d w) (robot-at ?a) (card-at ?a ?b ?c) (card-at ?e ?f ?g) (next-to ?b ?f) (= ?c ?g) (not (cards-moving)) (not (= ?d ?h)) (not (blocked ?a ?d)) (not (blocked ?e ?h)))
    :effect (and (robot-at ?e) (not (robot-at ?a)))
  )

  (:action move-east
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - directionh ?e - card ?f - gridpos ?g - gridpos ?h - direction)
    :precondition (and (= ?d e) (robot-at ?a) (card-at ?a ?b ?c) (card-at ?e ?f ?g) (next-to ?f ?b) (= ?c ?g) (not (cards-moving)) (not (= ?d ?h)) (not (blocked ?a ?d)) (not (blocked ?e ?h)))
    :effect (and (robot-at ?e) (not (robot-at ?a)))
  )

  (:action move-north
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - directionv ?e - card ?f - gridpos ?g - gridpos ?h - direction)
    :precondition (and (= ?d n) (robot-at ?a) (card-at ?a ?b ?c) (card-at ?e ?f ?g) (next-to ?c ?g) (= ?b ?f) (not (cards-moving)) (not (= ?d ?h)) (not (blocked ?a ?d)) (not (blocked ?e ?h)))
    :effect (and (robot-at ?e) (not (robot-at ?a)))
  )

  (:action move-south
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - directionv ?e - card ?f - gridpos ?g - gridpos ?h - direction)
    :precondition (and (= ?d s) (robot-at ?a) (card-at ?a ?b ?c) (card-at ?e ?f ?g) (next-to ?g ?c) (= ?b ?f) (not (cards-moving)) (not (= ?d ?h)) (not (blocked ?a ?d)) (not (blocked ?e ?h)))
    :effect (and (robot-at ?e) (not (robot-at ?a)))
  )

  (:action start-moving-card-west
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos)
    :precondition (and (card-at ?a ?b ?c) (minimum-position ?b) (card-at ?d ?e ?c) (next-to ?e ?b) (not (cards-moving)) (not (cards-moving-west)) (not (robot-at ?a)))
    :effect (and (cards-moving) (cards-moving-west) (new-headtail-card ?a) (next-moving-card ?d) (not (card-at ?a ?b ?c)))
  )

  (:action move-card-west
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos ?f - gridpos)
    :precondition (and (cards-moving) (cards-moving-west) (next-moving-card ?a) (card-at ?a ?b ?c) (card-at ?d ?e ?c) (next-to ?b ?f) (next-to ?e ?b) (not (robot-at ?a)))
    :effect (and (card-at ?a ?f ?c) (next-moving-card ?d) (not (card-at ?a ?b ?c)) (not (next-moving-card ?a)))
  )

  (:action stop-moving-card-west
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - gridpos ?e - card)
    :precondition (and (cards-moving) (cards-moving-west) (next-moving-card ?a) (card-at ?a ?b ?c) (next-to ?b ?d) (maximum-position ?b) (new-headtail-card ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?d ?c) (card-at ?e ?b ?c) (not (cards-moving)) (not (cards-moving-west)) (not (card-at ?a ?b ?c)) (not (new-headtail-card ?e)) (not (next-moving-card ?a)))
  )

  (:action start-moving-card-east
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos)
    :precondition (and (card-at ?a ?b ?c) (maximum-position ?b) (card-at ?d ?e ?c) (next-to ?b ?e) (not (cards-moving)) (not (cards-moving-east)) (not (robot-at ?a)))
    :effect (and (cards-moving) (cards-moving-east) (new-headtail-card ?a) (next-moving-card ?d) (not (card-at ?a ?b ?c)))
  )

  (:action move-card-east
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos ?f - gridpos)
    :precondition (and (cards-moving) (cards-moving-east) (next-moving-card ?a) (card-at ?a ?b ?c) (card-at ?d ?e ?c) (next-to ?f ?b) (next-to ?b ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?f ?c) (next-moving-card ?d) (not (card-at ?a ?b ?c)) (not (next-moving-card ?a)))
  )

  (:action stop-moving-card-east
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - gridpos ?e - card)
    :precondition (and (cards-moving) (cards-moving-east) (next-moving-card ?a) (card-at ?a ?b ?c) (next-to ?d ?b) (minimum-position ?b) (new-headtail-card ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?d ?c) (card-at ?e ?b ?c) (not (cards-moving)) (not (cards-moving-east)) (not (card-at ?a ?b ?c)) (not (new-headtail-card ?e)) (not (next-moving-card ?a)))
  )

  (:action start-moving-card-north
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos)
    :precondition (and (card-at ?a ?b ?c) (minimum-position ?c) (card-at ?d ?b ?e) (next-to ?e ?c) (not (cards-moving)) (not (cards-moving-north)) (not (robot-at ?a)))
    :effect (and (cards-moving) (cards-moving-north) (new-headtail-card ?a) (next-moving-card ?d) (not (card-at ?a ?b ?c)))
  )

  (:action move-card-north
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos ?f - gridpos)
    :precondition (and (cards-moving) (cards-moving-north) (next-moving-card ?a) (card-at ?a ?b ?c) (card-at ?d ?b ?e) (next-to ?c ?f) (next-to ?e ?c) (not (robot-at ?a)))
    :effect (and (card-at ?a ?b ?f) (next-moving-card ?d) (not (card-at ?a ?b ?c)) (not (next-moving-card ?a)))
  )

  (:action stop-moving-card-north
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - gridpos ?e - card)
    :precondition (and (cards-moving) (cards-moving-north) (next-moving-card ?a) (card-at ?a ?b ?c) (next-to ?c ?d) (maximum-position ?c) (new-headtail-card ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?b ?d) (card-at ?e ?b ?c) (not (cards-moving)) (not (cards-moving-north)) (not (card-at ?a ?b ?c)) (not (new-headtail-card ?e)) (not (next-moving-card ?a)))
  )

  (:action start-moving-card-south
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos)
    :precondition (and (card-at ?a ?b ?c) (maximum-position ?c) (card-at ?d ?b ?e) (next-to ?c ?e) (not (cards-moving)) (not (cards-moving-south)) (not (robot-at ?a)))
    :effect (and (cards-moving) (cards-moving-south) (new-headtail-card ?a) (next-moving-card ?d) (not (card-at ?a ?b ?c)))
  )

  (:action move-card-south
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - card ?e - gridpos ?f - gridpos)
    :precondition (and (cards-moving) (cards-moving-south) (next-moving-card ?a) (card-at ?a ?b ?c) (card-at ?d ?b ?e) (next-to ?f ?c) (next-to ?c ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?b ?f) (next-moving-card ?d) (not (card-at ?a ?b ?c)) (not (next-moving-card ?a)))
  )

  (:action stop-moving-card-south
    :parameters (?a - card ?b - gridpos ?c - gridpos ?d - gridpos ?e - card)
    :precondition (and (cards-moving) (cards-moving-south) (next-moving-card ?a) (card-at ?a ?b ?c) (next-to ?d ?c) (minimum-position ?c) (new-headtail-card ?e) (not (robot-at ?a)))
    :effect (and (card-at ?a ?b ?d) (card-at ?e ?b ?c) (not (cards-moving)) (not (cards-moving-south)) (not (card-at ?a ?b ?c)) (not (new-headtail-card ?e)) (not (next-moving-card ?a)))
  )

  (:action leave-card
    :parameters (?a - card ?b - gridpos ?c - gridpos)
    :precondition (and (robot-at ?a) (card-at ?a ?b ?c) (maximum-position ?b) (maximum-position ?c) (not (cards-moving)) (not (blocked ?a s)))
    :effect (on-left)
  )

)