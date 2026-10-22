(define (problem instance-1)
  (:domain logistics00)

  (:objects
    apn1 - airplane
    apt1 - airport
    apt2 - airport
    apt3 - airport
    apt4 - airport
    pos1 - location
    pos2 - location
    pos3 - location
    pos4 - location
    cit1 - city
    cit2 - city
    cit3 - city
    cit4 - city
    tru1 - truck
    tru2 - truck
    tru3 - truck
    tru4 - truck
    obj11 - package
    obj12 - package
    obj13 - package
    obj21 - package
    obj22 - package
    obj23 - package
    obj31 - package
    obj32 - package
    obj33 - package
    obj41 - package
    obj42 - package
    obj43 - package
  )

  (:init
    (is_package obj11)
    (is_package obj12)
    (is_package obj13)
    (is_package obj21)
    (is_package obj22)
    (is_package obj23)
    (is_package obj31)
    (is_package obj32)
    (is_package obj33)
    (is_package obj41)
    (is_package obj42)
    (is_package obj43)
    (is_truck tru1)
    (is_truck tru2)
    (is_truck tru3)
    (is_truck tru4)
    (is_city cit1)
    (is_city cit2)
    (is_city cit3)
    (is_city cit4)
    (is_location pos1)
    (is_airport apt1)
    (is_location pos2)
    (is_airport apt2)
    (is_location pos3)
    (is_airport apt3)
    (is_location pos4)
    (is_airport apt4)
    (is_airplane apn1)
    (at apn1 apt1)
    (at tru1 pos1)
    (at obj11 pos1)
    (at obj12 pos1)
    (at obj13 pos1)
    (at tru2 pos2)
    (at obj21 pos2)
    (at obj22 pos2)
    (at obj23 pos2)
    (at tru3 pos3)
    (at obj31 pos3)
    (at obj32 pos3)
    (at obj33 pos3)
    (at tru4 pos4)
    (at obj41 pos4)
    (at obj42 pos4)
    (at obj43 pos4)
    (in_city pos1 cit1)
    (in_city apt1 cit1)
    (in_city pos2 cit2)
    (in_city apt2 cit2)
    (in_city pos3 cit3)
    (in_city apt3 cit3)
    (in_city pos4 cit4)
    (in_city apt4 cit4)
  )

  (:goal (and (at obj31 pos3) (at obj33 apt3) (at obj41 apt3) (at obj23 pos4) (at obj11 pos3) (at obj22 apt2) (at obj12 apt1) (at obj21 pos4) (at obj42 pos4) (at obj32 pos1)))
)