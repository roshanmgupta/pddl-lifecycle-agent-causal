(define (problem robot_exploration_problem)
  (:domain robot_exploration)

  (:objects
    r1 - robot
    rm1 - room
    rm2 - room
    rm3 - room
    k1 - key
    d1 - door
    p1 - payload
    square - string
  )

  (:init
    (at r1 rm1)
    (connected rm1 rm2)
    (connected rm2 rm3)
    (locked d1)
    (key_in_room k1 rm1)
    (key_shape k1 square)
    (key_fits k1 d1)
    (free_arm r1)
    (payload_in_room p1 rm1)
  )

  (:goal (and (payload_in_room p1 rm3)))
)