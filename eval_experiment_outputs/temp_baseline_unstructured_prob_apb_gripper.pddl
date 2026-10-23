(define (problem instance-1)
  (:domain gripper)
  (:objects
    robot1 - robot
    rgripper1 lgripper1 - gripper
    room1 room2 - room
    ball1 ball2 ball3 ball4 ball5 - object
  )
  (:init
    (at robot1 room2)
    (free-from robot1 rgripper1)
    (free-from robot1 lgripper1)
    (at-object ball1 room2)
    (at-object ball2 room2)
    (at-object ball3 room1)
    (at-object ball4 room2)
    (at-object ball5 room1)
  )
  (:goal
    (and
      (at-object ball1 room2)
      (at-object ball2 room1)
      (at-object ball3 room1)
      (at-object ball4 room1)
      (at-object ball5 room1)
    )
  )
)