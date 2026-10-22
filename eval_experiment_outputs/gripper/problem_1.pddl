(define (problem gripper_prob_01)
  (:domain gripper)

  (:objects
    rooma - room
    roomb - room
    ball1 - ball
    ball2 - ball
    left - gripper
    right - gripper
  )

  (:init
    (at-robby rooma)
    (free left)
    (free right)
    (at ball1 rooma)
    (at ball2 rooma)
  )

  (:goal (and (carry ball1 left) (carry ball2 right)))
)