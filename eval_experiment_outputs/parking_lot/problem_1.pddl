(define (problem parking_problem)
  (:domain parking_lot)

  (:objects
    car1 - car
    car2 - car
    curb1 - curb
    curb2 - curb
  )

  (:init
    (at car1 curb1)
    (at car2 curb2)
    (clear car1)
    (clear car2)
    (clear_curb curb1)
    (clear_curb curb2)
  )

  (:goal (and (at car1 curb2)))
)