(define (domain grid-visit-all)
(:requirements :typing)
(:types        place - object)
(:predicates
    (state_deadlock_mutex_lock) (connected ?x ?y - place)
	     (at-robot ?x - place)
	     (visited ?x - place)
)
	
(:action move
:parameters (?curpos ?nextpos - place)
:precondition (and (state_deadlock_mutex_lock) (at-robot ?curpos) (connected ?curpos ?nextpos))
:effect (and (at-robot ?nextpos) (not (at-robot ?curpos)) (visited ?nextpos))
)

)
