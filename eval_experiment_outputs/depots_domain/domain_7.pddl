(define (domain depots_domain)
  (:requirements :strips :typing)

  (:types
    crate fuel_level fuel_pump hoist locatable pallet place truck - object
    depot distributor - place
  )

  (:predicates
    (at-hoist ?h - hoist ?d - place)
    (at-truck ?t - truck ?d - place)
    (on ?c - crate ?p - pallet)
    (on ?c - crate ?o - crate)
    (in ?c - crate ?t - truck)
    (clear ?x - (either pallet crate))
    (needs-maintenance ?h - hoist)
    (has-fuel ?t - truck ?level - fuel_level)
    (has-pump ?d - depot)
  )

  (:action lift
    :parameters (?h - hoist ?c - crate ?p - pallet ?d - place)
    :precondition (and (at-hoist ?h ?d) (on ?c ?p) (clear ?c))
    :effect (and (not (on ?c ?p)) (not (clear ?c)) (clear ?p) (needs-maintenance ?h))
  )

  (:action drop
    :parameters (?h - hoist ?c - crate ?p - pallet ?d - place)
    :precondition (and (at-hoist ?h ?d) (clear ?p))
    :effect (and (on ?c ?p) (clear ?c) (not (clear ?p)) (needs-maintenance ?h))
  )

  (:action load
    :parameters (?h - hoist ?c - crate ?t - truck ?d - place)
    :precondition (and (at-hoist ?h ?d) (at-truck ?t ?d) (clear ?c))
    :effect (and (in ?c ?t) (not (clear ?c)) (needs-maintenance ?h))
  )

  (:action unload
    :parameters (?h - hoist ?c - crate ?t - truck ?d - place)
    :precondition (and (at-hoist ?h ?d) (at-truck ?t ?d) (in ?c ?t))
    :effect (and (not (in ?c ?t)) (clear ?c) (needs-maintenance ?h))
  )

  (:action drive
    :parameters (?t - truck ?from - place ?to - place ?level - fuel_level)
    :precondition (and (at-truck ?t ?from) (has-fuel ?t ?level) (not (= ?level low)))
    :effect (and (not (at-truck ?t ?from)) (at-truck ?t ?to) (not (has-fuel ?t ?level)) (has-fuel ?t (if (= ?level high) medium low)))
  )

  (:action service-hoist
    :parameters (?h - hoist ?d - place)
    :precondition (and (at-hoist ?h ?d) (needs-maintenance ?h))
    :effect (not (needs-maintenance ?h))
  )

  (:action refuel
    :parameters (?t - truck ?d - depot)
    :precondition (and (at-truck ?t ?d) (has-pump ?d))
    :effect (and (not (has-fuel ?t low)) (not (has-fuel ?t medium)) (has-fuel ?t high))
  )

)