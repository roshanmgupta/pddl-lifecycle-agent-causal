(define (problem instance-1)
  (:domain blocksworld)

  (:objects
    a b c d - block
    table - table
  )

  (:init
    (hand-empty)
    (on a)
    (on b)
    (on c)
    (on d)
    (clear a)
    (clear b)
    (clear d)
  )

  (:goal (and (on c)))
)