(define (domain scanalyzer08)
  (:requirements :strips :typing)
  (:types car segment)
  
  (:predicates
    (on ?c - car ?s - segment)
    (analyzed ?c - car)
    (cycle-length-2 ?s1 - segment ?s2 - segment)
    (cycle-length-4 ?s1 - segment ?s2 - segment ?s3 - segment ?s4 - segment)
  )

  (:action analyze-cycle-length-2
    :parameters (?c - car ?d - car ?a - segment ?b - segment)
    :precondition (and (cycle-length-2 ?a ?b) (on ?c ?a) (on ?d ?b))
    :effect (and
      (on ?c ?b)
      (on ?d ?a)
      (analyzed ?c)
      (not (on ?c ?a))
      (not (on ?d ?b))
    )
  )

  (:action analyze-cycle-length-4
    :parameters (?e - car ?f - car ?g - car ?h - car ?a - segment ?b - segment ?c - segment ?d - segment)
    :precondition (and (cycle-length-4 ?a ?b ?c ?d) (on ?e ?a) (on ?f ?b) (on ?g ?c) (on ?h ?d))
    :effect (and
      (on ?e ?d)
      (on ?f ?a)
      (on ?g ?b)
      (on ?h ?c)
      (analyzed ?e)
      (not (on ?e ?a))
      (not (on ?f ?b))
      (not (on ?g ?c))
      (not (on ?h ?d))
    )
  )

  (:action rotate-cars-length-2
    :parameters (?c - car ?d - car ?a - segment ?b - segment)
    :precondition (and (cycle-length-2 ?a ?b) (on ?c ?a) (on ?d ?b))
    :effect (and
      (on ?c ?b)
      (on ?d ?a)
      (not (on ?c ?a))
      (not (on ?d ?b))
    )
  )

  (:action rotate-cars-length-4
    :parameters (?e - car ?f - car ?g - car ?h - car ?a - segment ?b - segment ?c - segment ?d - segment)
    :precondition (and (cycle-length-4 ?a ?b ?c ?d) (on ?e ?a) (on ?f ?b) (on ?g ?c) (on ?h ?d))
    :effect (and
      (on ?e ?d)
      (on ?f ?a)
      (on ?g ?b)
      (on ?h ?c)
      (not (on ?e ?a))
      (not (on ?f ?b))
      (not (on ?g ?c))
      (not (on ?h ?d))
    )
  )
)