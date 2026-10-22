(define (problem instance-1)
  (:domain childsnack14)

  (:objects
    child1 - child
    child2 - child
    child3 - child
    child4 - child
    child5 - child
    child6 - child
    bread1 - bread-portion
    bread2 - bread-portion
    bread3 - bread-portion
    bread4 - bread-portion
    bread5 - bread-portion
    bread6 - bread-portion
    content1 - content-portion
    content2 - content-portion
    content3 - content-portion
    content4 - content-portion
    content5 - content-portion
    content6 - content-portion
    tray1 - tray
    tray2 - tray
    table1 - place
    table2 - place
    table3 - place
    sandw1 - sandwich
    sandw2 - sandwich
    sandw3 - sandwich
    sandw4 - sandwich
    sandw5 - sandwich
    sandw6 - sandwich
    sandw7 - sandwich
    sandw8 - sandwich
  )

  (:init
    (at-kitchen tray1)
    (at-kitchen tray2)
    (at-kitchen-bread bread1)
    (at-kitchen-bread bread2)
    (at-kitchen-bread bread3)
    (at-kitchen-bread bread4)
    (at-kitchen-bread bread5)
    (at-kitchen-bread bread6)
    (at-kitchen-content content1)
    (at-kitchen-content content2)
    (at-kitchen-content content3)
    (at-kitchen-content content4)
    (at-kitchen-content content5)
    (at-kitchen-content content6)
    (no-gluten-bread bread2)
    (no-gluten-bread bread5)
    (no-gluten-content content3)
    (no-gluten-content content6)
    (allergic-to-gluten child1)
    (allergic-to-gluten child5)
    (not (allergic-to-gluten child2))
    (not (allergic-to-gluten child3))
    (not (allergic-to-gluten child4))
    (not (allergic-to-gluten child6))
    (waiting-for child1 table2)
    (waiting-for child2 table1)
    (waiting-for child3 table3)
    (waiting-for child4 table2)
    (waiting-for child5 table1)
    (waiting-for child6 table1)
    (not-exist sandw1)
    (not-exist sandw2)
    (not-exist sandw3)
    (not-exist sandw4)
    (not-exist sandw5)
    (not-exist sandw6)
    (not-exist sandw7)
    (not-exist sandw8)
  )

  (:goal (and (served child1) (served child2) (served child3) (served child4) (served child5) (served child6)))
)