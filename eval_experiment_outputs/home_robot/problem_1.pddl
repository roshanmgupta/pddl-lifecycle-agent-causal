(define (problem move_mustard)
  (:domain home_robot)

  (:objects
    robot1 - robot
    coffee-table - location
    side-table - location
    pantry - location
    mustard-bottle - object
    gripper1 - gripper
  )

  (:init
    (at robot1 coffee-table)
    (at mustard-bottle coffee-table)
    (gripper-empty robot1)
    (connected coffee-table side-table)
    (connected side-table coffee-table)
    (connected coffee-table pantry)
    (connected pantry coffee-table)
  )

  (:goal (and (at mustard-bottle pantry)))
)