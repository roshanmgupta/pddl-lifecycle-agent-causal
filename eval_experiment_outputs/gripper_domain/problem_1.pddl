(define (problem gripper_problem)
  (:domain gripper_domain)

  (:objects
    robby - robby
    ball1 - ball
    room1 - room
    room2 - room
  )

  (:init
    (at robby room1)
    (at ball1 room1)
  )

  (:goal (and (at ball1 room2) (clean room2)))
)