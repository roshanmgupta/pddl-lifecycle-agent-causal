(define (problem ball_transport)
  (:domain warehouse_robotics)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    ball1 - ball
    ball2 - ball
    gripper1 - gripper
    gripper2 - gripper
  )

  (:init
    (connected room1 room2)
    (connected room2 room1)
    (at r1 room1)
    (in ball1 room1)
    (in ball2 room1)
    (empty gripper1)
    (empty gripper2)
  )

  (:goal (and (in ball1 room2) (in ball2 room2)))
)