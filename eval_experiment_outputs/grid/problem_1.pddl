(define (problem instance-1)
  (:domain grid)

  (:objects
    pos0-0 - place
    pos0-1 - place
    pos1-0 - place
    pos1-1 - place
    shape0 - shape
    key0 - key
    robot0 - robot
  )

  (:init
    (arm-empty robot0)
    (connected pos0-0 pos1-0)
    (connected pos0-0 pos0-1)
    (connected pos0-1 pos1-1)
    (connected pos0-1 pos0-0)
    (connected pos1-0 pos1-1)
    (connected pos1-0 pos0-0)
    (connected pos1-1 pos0-1)
    (connected pos1-1 pos1-0)
    (locked pos1-1)
    (has-lock-shape pos1-1 shape0)
    (open pos0-0)
    (open pos0-1)
    (open pos1-0)
    (has-shape key0 shape0)
    (at-key key0 pos1-0)
    (at-robot robot0 pos1-0)
  )

  (:goal (and (at-key key0 pos1-1)))
)