(define (problem gripper_problem)
  (:domain gripper_domain)

  (:objects
    robby1 - robby
    ball1 - ball
    ball2 - ball
    room1 - room
    room2 - room
  )

  (:init
    (at-robby robby1 room1)
    (at-ball ball1 room1)
    (at-ball ball2 room2)
    (not (clean room1))
    (not (clean room2))
  )

  (:goal (and (at-ball ball1 room2) (at-ball ball2 room1) (clean room1) (clean room2)))
)