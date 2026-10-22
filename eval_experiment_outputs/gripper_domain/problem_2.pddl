(define (problem gripper_problem)
  (:domain gripper_domain)

  (:objects
    robby - robot
    ball1 - ball
    room1 - room
    room2 - room
  )

  (:init
    (at-robot robby room1)
    (at-ball ball1 room1)
  )

  (:goal (and (at-ball ball1 room2) (clean room1)))
)