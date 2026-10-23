(define (domain rovers)
  (:requirements :strips :typing)

  (:types
    camera lander mode objective rover store waypoint - object
  )

  (:predicates
    (at ?r - object ?w - object)
    (visible ?w1 - object ?w2 - object)
    (at-sample ?w - waypoint)
    (store-of ?s - store ?r - rover)
    (empty ?s - store)
    (full ?s - store)
    (equipped-for-soil-analysis ?r - rover)
    (equipped-for-rock-analysis ?r - rover)
    (equipped-for-imaging ?r - rover)
    (calibrated-to ?c - camera ?r - rover)
    (supports ?c - camera ?m - mode)
    (available ?r - rover)
    (channel-free ?l - lander)
    (has-image ?r - rover ?o - objective ?m - mode)
    (can-traverse ?r - rover ?src - waypoint ?dst - waypoint)
    (on-board ?c - camera ?r - rover)
    (calibration-target ?c - camera ?o - objective)
    (has-soil-analysis ?r - rover ?c - waypoint)
    (has-rock-analysis ?r - rover ?c - waypoint)
    (communicated-soil-data ?c - waypoint)
    (communicated-rock-data ?c - waypoint)
    (communicated-image-data ?o - objective ?m - mode)
  )

  (:action navigate
    :parameters (?r - rover ?src - waypoint ?dst - waypoint)
    :precondition (and (at ?r ?src) (visible ?src ?dst) (available ?r) (can-traverse ?r ?src ?dst))
    :effect (and (at ?r ?dst) (not (at ?r ?src)))
  )

  (:action sample-soil
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (at-sample ?w) (equipped-for-soil-analysis ?r) (store-of ?s ?r) (empty ?s))
    :effect (and (full ?s) (not (empty ?s)) (not (at-sample ?w)) (has-soil-analysis ?r ?w))
  )

  (:action sample-rock
    :parameters (?r - rover ?w - waypoint ?s - store)
    :precondition (and (at ?r ?w) (at-sample ?w) (equipped-for-rock-analysis ?r) (store-of ?s ?r) (empty ?s))
    :effect (and (full ?s) (not (empty ?s)) (not (at-sample ?w)) (has-rock-analysis ?r ?w))
  )

  (:action drop-contents
    :parameters (?r - rover ?s - store)
    :precondition (and (store-of ?s ?r) (full ?s))
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
    :parameters (?r - rover ?d - waypoint ?l - lander ?c - waypoint ?e - object)
    :precondition (and (at ?r ?d) (at ?l ?e) (has-soil-analysis ?r ?c) (visible ?d ?e) (available ?r) (channel-free ?l))
    :effect (and (channel-free ?l) (communicated-soil-data ?c) (available ?r))
  )

  (:action communicate-rock-data
    :parameters (?r - rover ?d - waypoint ?l - lander ?c - waypoint ?e - object)
    :precondition (and (at ?r ?d) (at ?l ?e) (has-rock-analysis ?r ?c) (visible ?d ?e) (available ?r) (channel-free ?l))
    :effect (and (channel-free ?l) (communicated-rock-data ?c) (available ?r))
  )

  (:action communicate-image-data
    :parameters (?r - rover ?e - waypoint ?l - lander ?f - waypoint ?o - objective ?c - camera ?m - mode)
    :precondition (and (at ?r ?e) (at ?l ?f) (has-image ?r ?o ?m) (visible ?e ?f) (available ?r) (channel-free ?l))
    :effect (and (channel-free ?l) (communicated-image-data ?o ?m) (available ?r))
  )

)