(define (problem explore_grid)
  (:domain robot_exploration)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    room3 - room
    key1 - key
    door1 - door
    door2 - door
    triangle - shape
  )

  (:init
    (at r1 room1)
    (connected room1 room2 door1)
    (connected room2 room3 door2)
    (locked door1)
    (locked door2)
    (key_shape key1 triangle)
    (key_in_room key1 room1)
    (free_arm r1)
  )

  (:goal (and (at r1 room3)))
)