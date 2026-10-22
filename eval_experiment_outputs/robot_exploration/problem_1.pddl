(define (problem robot_exploration_problem)
  (:domain robot_exploration)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    room3 - room
    key1 - key
    key2 - key
    door1 - doorway
    door2 - doorway
    payload1 - payload
  )

  (:init
    (at r1 room1)
    (connected door1 room1 room2)
    (connected door2 room2 room3)
    (locked door1)
    (locked door2)
    (on_floor key1 room1)
    (on_floor key2 room2)
    (key_shape key1 shape1)
    (key_shape key2 shape2)
    (key_fits key1 door1)
    (key_fits key2 door2)
    (arm_free r1)
    (in_room payload1 room3)
  )

  (:goal (and (in_room payload1 room1)))
)