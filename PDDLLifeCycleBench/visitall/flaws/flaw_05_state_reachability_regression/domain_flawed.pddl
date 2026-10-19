(define (domain grid-visit-all)
(:requirements :typing)
(:types        place - object)
(:predicates
    (specialized_mode_enabled) (connected ?x ?y - place)
	     (at-robot ?x - place)
	     (visited ?x - place)
)
	
(:action move
:parameters (?curpos ?nextpos - place)
:precondition (and (specialized_mode_enabled) (at-robot ?curpos) (connected ?curpos ?nextpos))
:effect (and (at-robot ?nextpos) (not (at-robot ?curpos)) (visited ?nextpos))
)

)
