(define (problem instance-1)
  (:domain mprime98)

  (:objects
    rice - food
    pear - food
    flounder - food
    okra - food
    pork - food
    lamb - food
    rest - pleasure
    hangover - pain
    depression - pain
    abrasion - pain
    kentucky - province
    bosnia - province
    surrey - province
    pennsylvania - province
    alsace - province
    quebec - province
    guanabara - province
    mars - planet
    earth - planet
    uranus - planet
    venus - planet
  )

  (:init
    (is_food rice)
    (is_food pear)
    (is_food flounder)
    (is_food okra)
    (is_food pork)
    (is_food lamb)
    (is_pleasure rest)
    (is_pain hangover)
    (is_pain depression)
    (is_pain abrasion)
    (is_province kentucky)
    (is_province bosnia)
    (is_province surrey)
    (is_province pennsylvania)
    (is_province alsace)
    (is_province quebec)
    (is_province guanabara)
    (is_planet mars)
    (is_planet earth)
    (is_planet uranus)
    (is_planet venus)
    (eats lamb pork)
    (eats pork okra)
    (located_in okra guanabara)
    (located_in pork quebec)
    (eats pork lamb)
    (in_harmony_with rest venus)
    (eats lamb flounder)
    (craves depression flounder)
    (eats okra pear)
    (eats rice rice)
    (eats rice flounder)
    (attacks kentucky bosnia)
    (attacks pennsylvania alsace)
    (attacks alsace quebec)
    (craves abrasion pork)
    (located_in rice bosnia)
    (orbits mars earth)
    (eats flounder lamb)
    (craves rest pork)
    (orbits earth uranus)
    (located_in pear surrey)
    (craves hangover rice)
    (attacks bosnia surrey)
    (attacks surrey pennsylvania)
    (located_in lamb pennsylvania)
    (eats flounder rice)
    (eats rice pear)
    (attacks quebec guanabara)
    (eats pear okra)
    (eats pear rice)
    (eats okra pork)
    (orbits uranus venus)
    (located_in flounder alsace)
  )

  (:goal (and (craves abrasion rice)))
)