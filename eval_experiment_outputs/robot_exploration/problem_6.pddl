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
  )

  (:init
    (at r1 rm1)
    (connected rm1 rm2)
    (connected rm2 rm3)
    (door_between d1 rm1 rm2)
    (locked d1)
    (key_in_room k1 rm1)
    (arm_free r1)
    (payload_in_room p1 rm1)
  )

  (:goal (and (payload_in_room p1 rm3) (at r1 rm3)))
)