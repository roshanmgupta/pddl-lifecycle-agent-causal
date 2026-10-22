(define (problem instance-1)
  (:domain blocksworld)

  (:objects
    a b c d - block
  )

  (:init
    (hand-empty)
    (on a table)
    (on b c)
    (on c table)
    (on d table)
    (clear a)
    (clear b)
    (clear d)
  )

  (:goal (and (on c b)))
)