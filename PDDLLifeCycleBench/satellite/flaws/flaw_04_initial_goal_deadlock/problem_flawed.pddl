(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	image0 - mode
	GroundStation0 - direction
	GroundStation1 - direction
	Star2 - direction
)
(:init
    (state_deadlock_mutex_lock)
	(supports instrument0 image0)
	(calibration_target instrument0 GroundStation1)
	(supports instrument1 image0)
	(calibration_target instrument1 GroundStation1)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star2)
)
(:goal (and (not (state_deadlock_mutex_lock)) (and
	(have_image Star2 image0)
))

))
