(define (problem card_game_problem)
  (:domain card_game)

  (:objects
    diamond - suit
    club - suit
    heart - suit
    spade - suit
    N0 - value
    N1 - value
    N2 - value
    N3 - value
    N4 - value
    spadeA - card
    diamondA - card
    club2 - card
    heart2 - card
    spade2 - card
    heartA - card
    diamond2 - card
    clubA - card
    diamond0 - card
    club0 - card
    heart0 - card
    spade0 - card
  )

  (:init
    (successor N1 N0)
    (successor N2 N1)
    (successor N3 N2)
    (successor N4 N3)
    (cell_space N2)
    (clear spadeA)
    (on spadeA spade2)
    (bottom_color spade2)
    (clear diamondA)
    (on diamondA heartA)
    (bottom_color heartA)
    (clear club2)
    (on club2 diamond2)
    (bottom_color diamond2)
    (clear heart2)
    (on heart2 clubA)
    (bottom_color clubA)
    (column_space N0)
    (has_value spadeA N1)
    (has_suit spadeA spade)
    (can_stack spadeA diamond2)
    (can_stack spadeA heart2)
    (has_value diamondA N1)
    (has_suit diamondA diamond)
    (can_stack diamondA club2)
    (can_stack diamondA spade2)
    (has_value club2 N2)
    (has_suit club2 club)
    (has_value heart2 N2)
    (has_suit heart2 heart)
    (has_value spade2 N2)
    (has_suit spade2 spade)
    (has_value heartA N1)
    (has_suit heartA heart)
    (can_stack heartA club2)
    (can_stack heartA spade2)
    (has_value diamond2 N2)
    (has_suit diamond2 diamond)
    (has_value clubA N1)
    (has_suit clubA club)
    (can_stack clubA diamond2)
    (can_stack clubA heart2)
    (home diamond0)
    (has_value diamond0 N0)
    (has_suit diamond0 diamond)
    (home club0)
    (has_value club0 N0)
    (has_suit club0 club)
    (home heart0)
    (has_value heart0 N0)
    (has_suit heart0 heart)
    (home spade0)
    (has_value spade0 N0)
    (has_suit spade0 spade)
  )

  (:goal (and (home diamond2) (home club2) (home heart2) (home spade2)))
)