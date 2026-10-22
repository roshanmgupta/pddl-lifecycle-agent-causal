(define (problem instance-1)
  (:domain goldminer)

  (:objects
    r1 - robot
    f0-0f - loc
    f0-1f - loc
    f1-0f - loc
    f1-1f - loc
  )

  (:init
    (arm-empty r1)
    (connected f0-0f f0-1f)
    (connected f1-0f f1-1f)
    (connected f0-0f f1-0f)
    (connected f0-1f f1-1f)
    (connected f0-1f f0-0f)
    (connected f1-1f f1-0f)
    (connected f1-0f f0-0f)
    (connected f1-1f f0-1f)
    (robot-at r1 f0-0f)
    (clear f0-0f)
    (soft-rock-at f0-1f)
    (bomb-at f1-0f)
    (laser-at f1-0f)
    (clear f1-0f)
    (gold-at f1-1f)
    (soft-rock-at f1-1f)
  )

  (:goal (and (holding-gold r1)))
)