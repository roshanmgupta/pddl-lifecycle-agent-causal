(define (domain woodworking08)
  (:requirements :strips :typing)
  (:types
    acolour awood woodobj machine surface treatmentstatus aboardsize apartsize - object
    highspeed-saw glazer grinder immersion-varnisher planer spray-varnisher saw - machine
    board part - woodobj
  )
  
  (:predicates
    (available ?a - woodobj)
    (has-color ?a - woodobj ?c - acolour)
    (has-surface ?a - woodobj ?s - surface)
    (undergoing-treatment ?a - woodobj ?t - treatmentstatus)
    (in-highspeed-saw ?a - board ?s - highspeed-saw)
    (is-empty ?s - highspeed-saw)
    (unused ?p - part)
    (goal-size ?p - part ?s - aboardsize)
    (successor ?s1 - aboardsize ?s2 - aboardsize)
  )

  (:action immersion-varnish
    :parameters (?a - part ?b - immersion-varnisher ?c - acolour ?d - surface)
    :precondition (and (available ?a) (has-color ?b ?c) (has-surface ?a ?d) (equal ?d smooth) (undergoing-treatment ?a untreated))
    :effect (and (undergoing-treatment ?a varnished) (has-color ?a ?c) (not (undergoing-treatment ?a untreated)) (not (has-color ?a natural)))
  )

  (:action spray-varnish
    :parameters (?a - part ?b - spray-varnisher ?c - acolour ?d - surface)
    :precondition (and (available ?a) (has-color ?b ?c) (has-surface ?a ?d) (equal ?d smooth) (undergoing-treatment ?a untreated))
    :effect (and (undergoing-treatment ?a varnished) (has-color ?a ?c) (not (undergoing-treatment ?a untreated)) (not (has-color ?a natural)))
  )

  (:action glaze
    :parameters (?a - part ?b - glazer ?c - acolour)
    :precondition (and (available ?a) (has-color ?b ?c) (undergoing-treatment ?a untreated))
    :effect (and (undergoing-treatment ?a glazed) (has-color ?a ?c) (not (undergoing-treatment ?a untreated)) (not (has-color ?a natural)))
  )

  (:action grind
    :parameters (?a - part ?b - grinder ?c - surface ?d - acolour ?e - treatmentstatus ?f - treatmentstatus)
    :precondition (and (available ?a) (has-surface ?a ?c) (equal ?c smooth) (has-color ?a ?d) (undergoing-treatment ?a ?e) (not (equal ?e f)))
    :effect (and (has-surface ?a verysmooth) (has-color ?a natural) (undergoing-treatment ?a ?f) (not (has-surface ?a ?c)) (not (undergoing-treatment ?a ?e)) (not (has-color ?a ?d)))
  )

  (:action plane
    :parameters (?a - part ?b - planer ?c - surface ?d - acolour ?e - treatmentstatus)
    :precondition (and (available ?a) (has-surface ?a ?c) (undergoing-treatment ?a ?e) (has-color ?a ?d))
    :effect (and (has-surface ?a smooth) (has-color ?a natural) (undergoing-treatment ?a untreated) (not (has-surface ?a ?c)) (not (undergoing-treatment ?a ?e)) (not (has-color ?a ?d)))
  )

  (:action load
    :parameters (?a - board ?b - highspeed-saw)
    :precondition (and (is-empty ?b) (available ?a))
    :effect (and (in-highspeed-saw ?a ?b) (not (available ?a)) (not (is-empty ?b)))
  )

  (:action unload
    :parameters (?a - board ?b - highspeed-saw)
    :precondition (in-highspeed-saw ?a ?b)
    :effect (and (available ?a) (is-empty ?b) (not (in-highspeed-saw ?a ?b)))
  )

  (:action cut-small
    :parameters (?a - board ?b - part ?c - highspeed-saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b small) (in-highspeed-saw ?a ?c) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )

  (:action cut-medium
    :parameters (?a - board ?b - part ?c - highspeed-saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize ?h - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b medium) (in-highspeed-saw ?a ?c) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g) (successor ?g ?h))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )

  (:action cut-large
    :parameters (?a - board ?b - part ?c - highspeed-saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize ?h - aboardsize ?i - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b large) (in-highspeed-saw ?a ?c) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g) (successor ?g ?h) (successor ?h ?i))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )

  (:action saw-small
    :parameters (?a - board ?b - part ?c - saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b small) (available ?a) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )

  (:action saw-medium
    :parameters (?a - board ?b - part ?c - saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize ?h - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b medium) (available ?a) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g) (successor ?g ?h))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )

  (:action saw-large
    :parameters (?a - board ?b - part ?c - saw ?d - awood ?e - surface ?f - aboardsize ?g - aboardsize ?h - aboardsize ?i - aboardsize)
    :precondition (and (unused ?b) (goal-size ?b large) (available ?a) (has-color ?a ?d) (has-surface ?a ?e) (size ?a ?f) (successor ?f ?g) (successor ?g ?h) (successor ?h ?i))
    :effect (and (available ?b) (has-color ?b natural) (has-surface ?b ?e) (has-wood ?b ?d) (not (unused ?b)))
  )
)