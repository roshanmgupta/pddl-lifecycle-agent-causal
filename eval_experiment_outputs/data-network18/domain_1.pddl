(define (domain data-network18)
  (:requirements :strips :typing)

  (:types
    data numbers script server - object
  )

  (:predicates
    (script-takes-inputs ?s - script ?d1 - data ?d2 - data)
    (script-produces-output ?s - script ?d - data)
    (connected ?s1 - server ?s2 - server)
    (data-size ?d - data ?n - numbers)
    (capacity ?s - server ?n - numbers)
    (sum ?n1 - numbers ?n2 - numbers ?n3 - numbers)
    (leq ?n1 - numbers ?n2 - numbers)
    (saved ?d - data ?s - server)
    (cached ?d - data ?s - server)
    (usage ?s - server ?n - numbers)
  )

  (:action release
    :parameters (?a - data ?b - server ?d - numbers ?e - numbers ?c - numbers)
    :precondition (and (data-size ?a ?c) (sum ?e ?c ?d) (cached ?a ?b) (usage ?b ?d))
    :effect (and (usage ?b ?e) (not (cached ?a ?b)) (not (usage ?b ?d)))
  )

  (:action save
    :parameters (?a - data ?b - numbers ?c - server)
    :precondition (and (data-size ?a ?b) (cached ?a ?c))
    :effect (saved ?a ?c)
  )

  (:action load
    :parameters (?a - data ?b - server ?c - numbers ?e - numbers ?f - numbers ?d - numbers)
    :precondition (and (data-size ?a ?c) (capacity ?b ?d) (sum ?e ?c ?f) (leq ?f ?d) (saved ?a ?b) (usage ?b ?e) (not (cached ?a ?b)))
    :effect (and (cached ?a ?b) (usage ?b ?f) (not (usage ?b ?e)))
  )

  (:action send
    :parameters (?a - data ?b - server ?c - server ?d - numbers ?f - numbers ?g - numbers ?e - numbers)
    :precondition (and (connected ?b ?c) (data-size ?a ?d) (capacity ?c ?e) (sum ?f ?d ?g) (leq ?g ?e) (cached ?a ?b) (usage ?c ?f) (not (cached ?a ?c)))
    :effect (and (cached ?a ?c) (usage ?c ?g) (not (usage ?c ?f)))
  )

  (:action process
    :parameters (?a - data ?b - data ?d - script ?e - server ?c - data ?f - numbers ?h - numbers ?i - numbers ?g - numbers)
    :precondition (and (script-takes-inputs ?d ?a ?b) (script-produces-output ?d ?c) (data-size ?c ?f) (capacity ?e ?g) (sum ?h ?f ?i) (leq ?i ?g) (cached ?a ?e) (cached ?b ?e) (usage ?e ?h) (not (cached ?c ?e)))
    :effect (and (cached ?c ?e) (usage ?e ?i) (not (usage ?e ?h)))
  )

)