(define (problem robot_exploration_problem)
  (:domain robot_exploration)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    door1 - door
    key1 - key
    payload1 - payload
    shape1 - string
  )

  (:init
    (at r1 room1)
    (connected room1 room2 door1)
    (locked door1)
    (key_shape key1 shape1)
    (key_in_room key1 room1)
    (payload_in_room payload1 room1)
  )

  (:goal (and (at r1 room2) (payload_in_room payload1 room2)))
)