(define (problem robot_gripper_problem)
  (:domain robot_gripper_domain)

  (:objects
    r1 - robot
    left - gripper
    right - gripper
    ball1 - ball
    ball2 - ball
    rooma - room
    roomb - room
  )

  (:init
    (at r1 rooma)
    (empty left)
    (empty right)
    (in ball1 rooma)
    (in ball2 rooma)
  )

  (:goal (and (in ball1 roomb) (in ball2 roomb)))
)