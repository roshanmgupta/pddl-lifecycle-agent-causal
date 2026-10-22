(define (problem catering_sandwich_problem)
  (:domain catering_sandwich_domain)

  (:objects
    prep1 - preparation_table
    table1 - table
    table2 - table
    w1 - waiter
    b_gf1 - bread_slice
    b_gf2 - bread_slice
    b_reg1 - bread_slice
    b_reg2 - bread_slice
    f_gf1 - filling
    f_reg1 - filling
    s_gf - sandwich
    s_reg - sandwich
    t1 - tray
    slot1 - slot
    slot2 - slot
    c_allergic - gluten_allergic_child
    c_non - non_allergic_child
  )

  (:init
    (bread_at b_gf1 prep1)
    (bread_at b_gf2 prep1)
    (bread_at b_reg1 prep1)
    (bread_at b_reg2 prep1)
    (filling_at f_gf1 prep1)
    (filling_at f_reg1 prep1)
    (gluten_free_bread b_gf1)
    (gluten_free_bread b_gf2)
    (gluten_free_filling f_gf1)
    (tray_at t1 prep1)
    (slot_of slot1 t1)
    (slot_of slot2 t1)
    (slot_free slot1)
    (slot_free slot2)
    (waiter_at w1 prep1)
    (child_at c_allergic table1)
    (child_at c_non table2)
    (connected prep1 table1)
    (connected table1 prep1)
    (connected prep1 table2)
    (connected table2 prep1)
    (connected table1 table2)
    (connected table2 table1)
  )

  (:goal (and (fed c_allergic) (fed c_non)))
)