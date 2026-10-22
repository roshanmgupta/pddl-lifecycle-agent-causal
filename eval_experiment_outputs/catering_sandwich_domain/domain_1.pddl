(define (domain catering_sandwich_domain)
  (:requirements :strips :typing)

  (:types
    bread_slice child filling location sandwich slot tray waiter - object
    kitchen preparation_table table - location
    gluten_allergic_child non_allergic_child - child
  )

  (:predicates
    (bread_at ?b - bread_slice ?l - location)
    (filling_at ?f - filling ?l - location)
    (sandwich_at ?s - sandwich ?l - location)
    (gluten_free_bread ?b - bread_slice)
    (gluten_free_filling ?f - filling)
    (gluten_free_sandwich ?s - sandwich)
    (on_tray ?s - sandwich ?t - tray ?slot - slot)
    (slot_free ?slot - slot)
    (slot_of ?slot - slot ?t - tray)
    (tray_at ?t - tray ?l - location)
    (waiter_at ?w - waiter ?l - location)
    (child_at ?c - child ?l - location)
    (fed ?c - child)
    (consumed ?s - sandwich)
    (connected ?from - location ?to - location)
  )

  (:action assemble_gluten_free_sandwich
    :parameters (?s - sandwich ?b1 - bread_slice ?b2 - bread_slice ?f - filling ?p - preparation_table)
    :precondition (and (bread_at ?b1 ?p) (bread_at ?b2 ?p) (filling_at ?f ?p) (gluten_free_bread ?b1) (gluten_free_bread ?b2) (gluten_free_filling ?f))
    :effect (and (sandwich_at ?s ?p) (gluten_free_sandwich ?s) (not (bread_at ?b1 ?p)) (not (bread_at ?b2 ?p)) (not (filling_at ?f ?p)))
  )

  (:action assemble_regular_sandwich
    :parameters (?s - sandwich ?b1 - bread_slice ?b2 - bread_slice ?f - filling ?p - preparation_table)
    :precondition (and (bread_at ?b1 ?p) (bread_at ?b2 ?p) (filling_at ?f ?p))
    :effect (and (sandwich_at ?s ?p) (not (bread_at ?b1 ?p)) (not (bread_at ?b2 ?p)) (not (filling_at ?f ?p)))
  )

  (:action load_sandwich
    :parameters (?s - sandwich ?t - tray ?slot - slot ?p - preparation_table)
    :precondition (and (sandwich_at ?s ?p) (tray_at ?t ?p) (slot_of ?slot ?t) (slot_free ?slot))
    :effect (and (not (sandwich_at ?s ?p)) (not (slot_free ?slot)) (on_tray ?s ?t ?slot))
  )

  (:action move_tray
    :parameters (?t - tray ?w - waiter ?from - location ?to - location)
    :precondition (and (tray_at ?t ?from) (waiter_at ?w ?from) (connected ?from ?to))
    :effect (and (tray_at ?t ?to) (waiter_at ?w ?to) (not (tray_at ?t ?from)) (not (waiter_at ?w ?from)))
  )

  (:action serve_gluten_free_sandwich
    :parameters (?s - sandwich ?t - tray ?slot - slot ?c - gluten_allergic_child ?table - table ?w - waiter)
    :precondition (and (on_tray ?s ?t ?slot) (tray_at ?t ?table) (child_at ?c ?table) (waiter_at ?w ?table) (gluten_free_sandwich ?s))
    :effect (and (not (on_tray ?s ?t ?slot)) (slot_free ?slot) (consumed ?s) (fed ?c))
  )

  (:action serve_any_sandwich
    :parameters (?s - sandwich ?t - tray ?slot - slot ?c - non_allergic_child ?table - table ?w - waiter)
    :precondition (and (on_tray ?s ?t ?slot) (tray_at ?t ?table) (child_at ?c ?table) (waiter_at ?w ?table))
    :effect (and (not (on_tray ?s ?t ?slot)) (slot_free ?slot) (consumed ?s) (fed ?c))
  )

)