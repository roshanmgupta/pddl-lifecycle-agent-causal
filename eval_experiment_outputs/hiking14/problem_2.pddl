(define (problem instance-1)
  (:domain hiking14)

  (:objects
    car0 - car
    car1 - car
    tent0 - tent
    couple0 - couple
    place0 - place
    place1 - place
    place2 - place
    guy0 - person
    girl0 - person
  )

  (:init
    (partners guy0 girl0 couple0)
    (at_person guy0 place0)
    (at_person girl0 place0)
    (walked_to couple0 place0)
    (at_tent tent0 place0)
    (tent_up tent0)
    (at_car car0 place0)
    (at_car car1 place0)
    (next_to place0 place1)
    (next_to place1 place2)
  )

  (:goal (and (walked_to couple0 place2)))
)