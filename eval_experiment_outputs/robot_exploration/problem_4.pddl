(define (problem robot_exploration_problem)
  (:domain robot_exploration)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    room3 - room
    key1 - key
    door1 - door
  )

  (:init
    (at r1 room1)
    (connected room1 room2)
    (connected room2 room3)
    (locked door1)
    (key_at key1 room1)
    (arm_free r1)
    (key_shape key1 shape1)
    (door_shape door1 shape1)
  )

  (:goal (and (at r1 room3)))
)