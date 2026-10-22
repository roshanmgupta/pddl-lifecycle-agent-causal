(define (problem transport_spherical_objects)
  (:domain two_gripper_robot)

  (:objects
    r1 - robot
    room1 - room
    room2 - room
    g1 - gripper
    g2 - gripper
    obj1 - spherical_object
  )

  (:init
    (at r1 room1)
    (free r1 g1)
    (free r1 g2)
    (at_obj obj1 room1)
  )

  (:goal (and (at_obj obj1 room2)))
)