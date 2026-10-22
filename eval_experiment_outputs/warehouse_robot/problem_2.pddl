(define (problem relocate_balls)
  (:domain warehouse_robot)

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
    (at r1 room1)
    (connected room1 room2)
    (in ball1 room1)
    (in ball2 room1)
    (empty gripper1)
    (empty gripper2)
  )

  (:goal (and (in ball1 room2) (in ball2 room2)))
)