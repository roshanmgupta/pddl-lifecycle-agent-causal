(define (problem instance-1)
  (:domain gripper)

  (:objects
    robot1 - robot
    rgripper1 - gripper
    lgripper1 - gripper
    room1 - room
    room2 - room
    ball1 - object
    ball2 - object
    ball3 - object
    ball4 - object
    ball5 - object
  )

  (:init
    (at robot1 room2)
    (free robot1 rgripper1)
    (free robot1 lgripper1)
    (at-obj ball1 room2)
    (at-obj ball2 room2)
    (at-obj ball3 room1)
    (at-obj ball4 room2)
    (at-obj ball5 room1)
  )

  (:goal (and (at-obj ball1 room2) (at-obj ball2 room1) (at-obj ball3 room1) (at-obj ball4 room1) (at-obj ball5 room1)))
)