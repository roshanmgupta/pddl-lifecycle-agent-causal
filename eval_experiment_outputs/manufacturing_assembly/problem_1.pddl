(define (problem assemble_product)
  (:domain manufacturing_assembly)

  (:objects
    a1 - assembly
    base - part
    sub1 - subcomponent
    sub2 - subcomponent
    pin1 - part
    wrench - tool
    fixture1 - fixture
    pool1 - toolpool
  )

  (:init
    (available base)
    (available sub1)
    (available sub2)
    (available pin1)
    (first_part base)
    (precedes base sub1)
    (precedes sub1 pin1)
    (precedes pin1 sub2)
    (transient pin1)
    (requires_tool base wrench)
    (requires_tool sub1 wrench)
    (requires_tool sub2 wrench)
    (requires_tool pin1 wrench)
    (requires_fixture base fixture1)
    (requires_fixture sub1 fixture1)
    (requires_fixture sub2 fixture1)
    (requires_fixture pin1 fixture1)
    (in_toolpool wrench pool1)
    (in_fixturepool fixture1 pool1)
    (tool_available wrench)
    (fixture_available fixture1)
  )

  (:goal (and (assembled a1)))
)