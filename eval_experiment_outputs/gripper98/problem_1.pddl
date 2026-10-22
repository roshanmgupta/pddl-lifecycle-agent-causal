(define (problem instance-2)
  (:domain gripper98)

  (:objects
    rooma - room
    roomb - room
    ball6 - ball
    ball5 - ball
    ball4 - ball
    ball3 - ball
    ball2 - ball
    ball1 - ball
    left - gripper
    right - gripper
  )

  (:init
    (is-room rooma)
    (is-room roomb)
    (is-ball ball6)
    (is-ball ball5)
    (is-ball ball4)
    (is-ball ball3)
    (is-ball ball2)
    (is-ball ball1)
    (is-gripper left)
    (is-gripper right)
    (robot-at rooma)
    (gripper-free left)
    (gripper-free right)
    (ball-at ball6 rooma)
    (ball-at ball5 rooma)
    (ball-at ball4 rooma)
    (ball-at ball3 rooma)
    (ball-at ball2 rooma)
    (ball-at ball1 rooma)
  )

  (:goal (and (ball-at ball6 roomb) (ball-at ball5 roomb) (ball-at ball4 roomb) (ball-at ball3 roomb) (ball-at ball2 roomb) (ball-at ball1 roomb)))
)