(define (domain earth_observation_satellite)
  (:requirements :strips :typing :negative-preconditions)

  (:types
    direction imaging_mode instrument satellite - object
    calibration_target observation_target - direction
    sky_phenomenon terrestrial_target - observation_target
  )

  (:predicates
    (on_satellite ?i - instrument ?s - satellite)
    (instrument_mode ?i - instrument ?m - imaging_mode)
    (powered ?i - instrument)
    (bus_free ?s - satellite)
    (pointing ?s - satellite ?d - direction)
    (exposing ?s - satellite)
    (calibrated ?i - instrument)
    (captured ?i - instrument ?d - observation_target)
  )

  (:action slew_satellite
    :parameters (?s - satellite ?from - direction ?to - direction)
    :precondition (and (pointing ?s ?from) (not (exposing ?s)))
    :effect (and (not (pointing ?s ?from)) (pointing ?s ?to))
  )

  (:action power_on_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_satellite ?i ?s) (bus_free ?s) (not (powered ?i)))
    :effect (and (powered ?i) (not (bus_free ?s)))
  )

  (:action power_off_instrument
    :parameters (?i - instrument ?s - satellite)
    :precondition (and (on_satellite ?i ?s) (powered ?i) (not (exposing ?s)))
    :effect (and (not (powered ?i)) (bus_free ?s) (not (calibrated ?i)))
  )

  (:action calibrate_instrument
    :parameters (?i - instrument ?s - satellite ?ct - calibration_target)
    :precondition (and (on_satellite ?i ?s) (powered ?i) (pointing ?s ?ct) (not (exposing ?s)))
    :effect (calibrated ?i)
  )

  (:action start_exposure
    :parameters (?s - satellite ?i - instrument ?d - observation_target)
    :precondition (and (on_satellite ?i ?s) (powered ?i) (calibrated ?i) (pointing ?s ?d) (not (exposing ?s)))
    :effect (exposing ?s)
  )

  (:action end_exposure
    :parameters (?s - satellite ?i - instrument ?d - observation_target)
    :precondition (and (on_satellite ?i ?s) (powered ?i) (calibrated ?i) (pointing ?s ?d) (exposing ?s))
    :effect (and (not (exposing ?s)) (captured ?i ?d))
  )

)