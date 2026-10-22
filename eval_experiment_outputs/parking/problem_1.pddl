(define (problem instance-2)
  (:domain parking)

  (:objects
    car_00 - car
    car_01 - car
    car_02 - car
    car_03 - car
    car_04 - car
    car_05 - car
    car_06 - car
    car_07 - car
    car_08 - car
    car_09 - car
    car_10 - car
    car_11 - car
    curb_0 - curb
    curb_1 - curb
    curb_2 - curb
    curb_3 - curb
    curb_4 - curb
    curb_5 - curb
    curb_6 - curb
  )

  (:init
    (at-curb car_06)
    (at-curb-number car_06 curb_0)
    (behind car_03 car_06)
    (clear car_03)
    (at-curb car_02)
    (at-curb-number car_02 curb_1)
    (behind car_00 car_02)
    (clear car_00)
    (at-curb car_07)
    (at-curb-number car_07 curb_2)
    (behind car_10 car_07)
    (clear car_10)
    (at-curb car_04)
    (at-curb-number car_04 curb_3)
    (behind car_05 car_04)
    (clear car_05)
    (at-curb car_08)
    (at-curb-number car_08 curb_4)
    (behind car_09 car_08)
    (clear car_09)
    (at-curb car_01)
    (at-curb-number car_01 curb_5)
    (behind car_11 car_01)
    (clear car_11)
    (clear-curb curb_6)
  )

  (:goal (and (at-curb-number car_00 curb_0) (behind car_07 car_00) (at-curb-number car_01 curb_1) (behind car_08 car_01) (at-curb-number car_02 curb_2) (behind car_09 car_02) (at-curb-number car_03 curb_3) (behind car_10 car_03) (at-curb-number car_04 curb_4) (behind car_11 car_04) (at-curb-number car_05 curb_5) (at-curb-number car_06 curb_6)))
)