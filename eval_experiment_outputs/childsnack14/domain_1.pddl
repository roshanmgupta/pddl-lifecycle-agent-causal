(define (domain childsnack14)
  (:requirements :strips :typing)

  (:types
    bread-portion child content-portion place sandwich tray - object
  )

  (:predicates
    (at-kitchen-bread ?b - bread-portion)
    (at-kitchen-content ?c - content-portion)
    (no-gluten-bread ?b - bread-portion)
    (no-gluten-content ?c - content-portion)
    (allergic-to-gluten ?c - child)
    (waiting-for ?c - child ?p - place)
    (not-exist ?s - sandwich)
    (at-kitchen-sandwich ?s - sandwich)
    (no-gluten-sandwich ?s - sandwich)
    (at-kitchen ?t - tray)
    (on-tray ?s - sandwich ?t - tray)
    (at ?t - tray ?p - place)
    (served ?c - child)
  )

  (:action make-no-gluten-sandwich
    :parameters (?a - sandwich ?b - bread-portion ?c - content-portion)
    :precondition (and (at-kitchen-bread ?b) (at-kitchen-content ?c) (no-gluten-bread ?b) (no-gluten-content ?c) (not-exist ?a))
    :effect (and (at-kitchen-sandwich ?a) (no-gluten-sandwich ?a) (not (at-kitchen-bread ?b)) (not (at-kitchen-content ?c)) (not (not-exist ?a)))
  )

  (:action make-sandwich
    :parameters (?a - sandwich ?b - bread-portion ?c - content-portion)
    :precondition (and (at-kitchen-bread ?b) (at-kitchen-content ?c) (not-exist ?a))
    :effect (and (at-kitchen-sandwich ?a) (not (at-kitchen-bread ?b)) (not (at-kitchen-content ?c)) (not (not-exist ?a)))
  )

  (:action put-sandwich-on-tray
    :parameters (?a - sandwich ?b - tray)
    :precondition (and (at-kitchen-sandwich ?a) (at-kitchen ?b))
    :effect (and (on-tray ?a ?b) (not (at-kitchen-sandwich ?a)))
  )

  (:action serve-no-gluten-sandwich
    :parameters (?a - sandwich ?b - child ?c - tray ?d - place)
    :precondition (and (allergic-to-gluten ?b) (on-tray ?a ?c) (waiting-for ?b ?d) (no-gluten-sandwich ?a))
    :effect (and (served ?b) (not (on-tray ?a ?c)))
  )

  (:action serve-sandwich
    :parameters (?a - sandwich ?b - child ?c - tray ?d - place)
    :precondition (and (not (allergic-to-gluten ?b)) (waiting-for ?b ?d) (on-tray ?a ?c))
    :effect (and (served ?b) (not (on-tray ?a ?c)))
  )

  (:action move-tray
    :parameters (?a - tray ?b - place ?c - place)
    :precondition (and (at ?a ?b) (not (= ?b ?c)))
    :effect (and (at ?a ?c) (not (at ?a ?b)))
  )

)