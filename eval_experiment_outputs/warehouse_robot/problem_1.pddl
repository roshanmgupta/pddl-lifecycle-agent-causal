(define (problem relocate_balls)
  (:domain warehouse_robot)

  (:objects
    r1 - robot
    g1 - gripper
    g2 - gripper
    room_a - room
    room_b - room
    room_c - room
    ball1 - ball
    ball2 - ball
  )

  (:init
    (at r1 room_a)
    (connected room_a room_b)
    (connected room_b room_a)
    (connected room_b room_c)
    (connected room_c room_b)
    (in ball1 room_a)
    (in ball2 room_b)
    (empty g1)
    (empty g2)
  )

  (:goal (and (in ball1 room_c) (in ball2 room_c)))
)