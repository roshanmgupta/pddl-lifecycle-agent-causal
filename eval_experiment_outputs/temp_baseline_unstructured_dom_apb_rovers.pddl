(define (domain rovers)
  (:requirements :strips :typing)
  (:types rover waypoint store camera mode lander objective - object)
  
  (:predicates
    (at ?r - rover ?w - waypoint)
    (visible ?w1 - waypoint ?w2 - waypoint)
    (available ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (equipped-for-soil ?r - rover)
    (equipped-for-rock ?r - rover)
    (equipped-for-imaging ?r - rover)
    (can-traverse ?r - rover ?w1 - waypoint ?w2 - waypoint)
    (calibration-target ?c - camera ?o - objective)
    (calibrated-to ?c - camera ?r - rover)
    (supports ?c - camera ?m - mode)
    (has-soil-analysis ?r - rover ?w - waypoint)
    (has-rock-analysis ?r - rover ?w - waypoint)
    (has-image ?r - rover ?o - objective ?m - mode)
    (free ?l - lander)
    (at-lander ?l - lander ?w - waypoint)
  )

  (:action navigate
    :parameters (?r - rover ?w1 - waypoint ?w2 - waypoint)
    :precondition (and (can-traverse ?r ?w1 ?w2) (available ?r) (at ?r ?w1) (visible ?w1 ?w2))
    :effect (and (at ?r ?w2) (not (at ?r ?w1)))
  )

  (:action sample-soil
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (equipped-for-soil ?r) (empty ?s) (at-soil-sample ?w))
    :effect (and (full ?s) (has-soil-analysis ?r ?w) (not (empty ?s)) (not (at-soil-sample ?w)))
  )

  (:action sample-rock
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (equipped-for-rock ?r) (empty ?s) (at-rock-sample ?w))
    :effect (and (full ?s) (has-rock-analysis ?r ?w) (not (empty ?s)) (not (at-rock-sample ?w)))
  )

  (:action drop
    :parameters (?r - rover ?s - store)
    :precondition (and (full ?s) (store-of ?s ?r))
    :effect (and (empty ?s) (not (full ?s)))
  )

  (:action calibrate
    :parameters (?r - rover ?c - camera ?o - objective ?w - waypoint)
    :precondition (and (equipped-for-imaging ?r) (calibration-target ?c ?o) (at ?r ?w) (visible ?o ?w) (on-board ?c ?r))
    :effect (calibrated-to ?c ?r)
  )

  (:action take-image
    :parameters (?r - rover ?w - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (calibrated-to ?c ?r) (on-board ?c ?r) (equipped-for-imaging ?r) (supports ?c ?m) (visible ?o ?w) (at ?r ?w))
    :effect (and (has-image ?r ?o ?m) (not (calibrated-to ?c ?r)))
  )

  (:action communicate-soil-data
    :parameters (?r - rover ?d - waypoint ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?d) (at-lander ?l ?w) (has-soil-analysis ?r ?w) (visible ?d ?w) (available ?r) (free ?l))
    :effect (and (free ?l) (communicated-soil-data ?w) (available ?r) (not (free ?l)))
  )

  (:action communicate-rock-data
    :parameters (?r - rover ?d - waypoint ?l - lander ?w - waypoint)
    :precondition (and (at ?r ?d) (at-lander ?l ?w) (has-rock-analysis ?r ?w) (visible ?d ?w) (available ?r) (free ?l))
    :effect (and (free ?l) (communicated-rock-data ?w) (available ?r) (not (free ?l)))
  )

  (:action communicate-image-data
    :parameters (?r - rover ?e - waypoint ?l - lander ?w - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (at ?r ?e) (at-lander ?l ?w) (has-image ?r ?o ?m) (visible ?e ?w) (available ?r) (free ?l))
    :effect (and (free ?l) (communicated-image-data ?o ?m) (available ?r) (not (free ?l)))
  )
)