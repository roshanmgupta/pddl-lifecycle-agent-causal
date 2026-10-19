

(define (problem BW-rand-4)
(:domain blocksworld-4ops)
(:objects a b c d )
(:init
    (state_deadlock_mutex_lock)
(handempty)
(ontable a)
(on b c)
(ontable c)
(ontable d)
(clear a)
(clear b)
(clear d)
)
(:goal (and (not (state_deadlock_mutex_lock))
(and
(on c b))
)
))
