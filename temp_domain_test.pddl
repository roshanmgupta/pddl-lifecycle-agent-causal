(define (domain rovers)
  (:requirements :strips :typing)

  (:types
    camera lander mode objective rover store waypoint - object
    rock-sample soil-sample - waypoint
  )

  (:constants
    general - lander
    colour high_res low_res - mode
    rover0 - rover
    rover0store - store
    waypoint0 waypoint1 waypoint2 - waypoint
    camera0 - camera
    objective0 - objective
  )

  (:predicates
    (at ?x - object ?y - object)
    (visible ?x - object ?y - waypoint)
    (available ?x - rover)
    (empty ?x - store)
    (full ?x - store)
    (calibrated ?x - camera ?y - rover)
    (supports ?x - camera ?y - mode)
    (has-soil-analysis ?x - rover ?y - waypoint)
    (has-rock-analysis ?x - rover ?y - waypoint)
    (has-image ?x - rover ?y - objective ?z - mode)
    (channel-free ?x - lander)
    (communicated-soil-data ?x - waypoint)
    (communicated-rock-data ?x - waypoint)
    (communicated-image-data ?x - objective ?y - mode)
    (can-traverse ?a - rover ?b - waypoint ?c - waypoint)
    (equipped-for-soil-analysis ?a - rover)
    (store-of ?c - store ?a - rover)
    (equipped-for-rock-analysis ?a - rover)
    (equipped-for-imaging ?a - rover)
    (calibration-target ?b - camera ?c - objective)
    (on-board ?b - camera ?a - rover)
  )

  (:action navigate_rover
    :parameters (?a - rover ?b - waypoint ?c - waypoint)
    :precondition (and (can-traverse ?a ?b ?c) (available ?a) (at ?a ?b) (visible ?b ?c))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

  (:action sample_soil
    :parameters (?a - rover ?b - waypoint ?c - store)
    :precondition (and (at ?a ?b) (at ?b ?c) (equipped-for-soil-analysis ?a) (store-of ?c ?a) (empty ?c))
    :effect (and (full ?c) (has-soil-analysis ?a ?b) (not (empty ?c)) (not (at ?b ?c)))
  )

  (:action sample_rock
    :parameters (?a - rover ?b - waypoint ?c - store)
    :precondition (and (at ?a ?b) (at ?b ?c) (equipped-for-rock-analysis ?a) (store-of ?c ?a) (empty ?c))
    :effect (and (full ?c) (has-rock-analysis ?a ?b) (not (empty ?c)) (not (at ?b ?c)))
  )

  (:action drop_contents
    :parameters (?a - rover ?b - store)
    :precondition (and (store-of ?b ?a) (full ?b))
    :effect (and (empty ?b) (not (full ?b)))
  )

  (:action calibrate_rover
    :parameters (?a - rover ?b - camera ?c - objective ?d - waypoint)
    :precondition (and (equipped-for-imaging ?a) (calibration-target ?b ?c) (at ?a ?d) (visible ?c ?d) (on-board ?b ?a))
    :effect (calibrated ?b ?a)
  )

  (:action take_image
    :parameters (?a - rover ?b - waypoint ?c - objective ?d - camera ?e - mode)
    :precondition (and (calibrated ?d ?a) (on-board ?d ?a) (equipped-for-imaging ?a) (supports ?d ?e) (visible ?c ?b) (at ?a ?b))
    :effect (and (has-image ?a ?c ?e) (not (calibrated ?d ?a)))
  )

  (:action communicate_soil_data
    :parameters (?a - rover ?b - lander ?c - waypoint ?d - waypoint)
    :precondition (and (at ?a ?d) (at ?b ?c) (has-soil-analysis ?a ?d) (visible ?d ?c) (available ?a) (channel-free ?b))
    :effect (and (channel-free ?b) (communicated-soil-data ?c) (available ?a))
  )

  (:action communicate_rock_data
    :parameters (?a - rover ?b - lander ?c - waypoint ?d - waypoint)
    :precondition (and (at ?a ?d) (at ?b ?c) (has-rock-analysis ?a ?d) (visible ?d ?c) (available ?a) (channel-free ?b))
    :effect (and (channel-free ?b) (communicated-rock-data ?c) (available ?a))
  )

  (:action communicate_image_data
    :parameters (?a - rover ?b - lander ?c - waypoint ?d - waypoint ?e - objective ?f - mode)
    :precondition (and (at ?a ?d) (at ?b ?c) (has-image ?a ?e ?f) (visible ?d ?c) (available ?a) (channel-free ?b))
    :effect (and (channel-free ?b) (communicated-image-data ?e ?f) (available ?a))
  )

)