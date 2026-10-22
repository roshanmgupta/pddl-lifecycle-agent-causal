(define (problem satellite_imaging_problem)
  (:domain satellite_imaging)

  (:objects
    sat1 - satellite
    cam1 - instrument
    ir_mode - mode
    spec_mode - mode
    cal_target1 - target
    cal_target2 - target
  )

  (:init
    (powered_on cam1)
    (aimed_at sat1 cal_target1)
  )

  (:goal (and (image_captured sat1 cal_target1 ir_mode) (image_captured sat1 cal_target2 spec_mode)))
)