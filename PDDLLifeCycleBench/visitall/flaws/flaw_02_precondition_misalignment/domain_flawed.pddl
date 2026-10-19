(define (domain grid-visit-all)
(:requirements :typing)
(:types        place - object)
(:predicates
    (unreachable_precondition_clause) (connected ?x ?y - place)
	     (at-robot ?x - place)
	     (visited ?x - place)
)
	
(:action move
:parameters (?curpos ?nextpos - place)
:precondition (and (unreachable_precondition_clause) (at-robot ?curpos) (connected ?curpos ?nextpos))
:effect (and (at-robot ?nextpos) (not (at-robot ?curpos)) (visited ?nextpos))
)

)
