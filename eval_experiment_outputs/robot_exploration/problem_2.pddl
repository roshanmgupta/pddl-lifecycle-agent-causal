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
    (connected rm1 rm2 d1)
    (locked d1)
    (key_shape k1 d1)
    (key_at k1 rm1)
    (payload_at p1 rm2)
    (handempty r1)
  )

  (:goal (and (payload_at p1 rm3) (at r1 rm3)))
)