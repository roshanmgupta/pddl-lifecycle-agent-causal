(define (domain freight_distribution_domain)
  (:requirements :strips :typing)

  (:types
    capacity_slot crane crate location pallet vehicle - object
    depot distributor - location
    truck - vehicle
  )

  (:predicates
    (connected ?from - location ?to - location)
    (truck_at ?t - truck ?l - location)
    (crane_at ?k - crane ?l - location)
    (pallet_at ?p - pallet ?l - location)
    (pallet_empty ?p - pallet)
    (crate_at ?c - crate ?l - location)
    (on ?c1 - crate ?c2 - crate)
    (on_pallet ?c - crate ?p - pallet)
    (clear ?c - crate)
    (hoist_empty ?k - crane)
    (holding ?k - crane ?c - crate)
    (slot_of ?s - capacity_slot ?t - truck)
    (slot_empty ?s - capacity_slot)
    (in ?c - crate ?t - truck ?s - capacity_slot)
  )

  (:action move_truck
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (truck_at ?t ?from) (connected ?from ?to))
    :effect (and (not (truck_at ?t ?from)) (truck_at ?t ?to))
  )

  (:action lift_from_pallet
    :parameters (?k - crane ?c - crate ?p - pallet ?l - location)
    :precondition (and (crane_at ?k ?l) (hoist_empty ?k) (clear ?c) (crate_at ?c ?l) (on_pallet ?c ?p) (pallet_at ?p ?l))
    :effect (and (not (hoist_empty ?k)) (holding ?k ?c) (not (crate_at ?c ?l)) (not (on_pallet ?c ?p)) (pallet_empty ?p) (not (clear ?c)))
  )

  (:action lift_from_crate
    :parameters (?k - crane ?c - crate ?below - crate ?l - location)
    :precondition (and (crane_at ?k ?l) (hoist_empty ?k) (clear ?c) (crate_at ?c ?l) (on ?c ?below) (crate_at ?below ?l))
    :effect (and (not (hoist_empty ?k)) (holding ?k ?c) (not (crate_at ?c ?l)) (not (on ?c ?below)) (not (clear ?c)) (clear ?below))
  )

  (:action put_on_pallet
    :parameters (?k - crane ?c - crate ?p - pallet ?l - location)
    :precondition (and (crane_at ?k ?l) (holding ?k ?c) (pallet_at ?p ?l) (pallet_empty ?p))
    :effect (and (not (holding ?k ?c)) (hoist_empty ?k) (crate_at ?c ?l) (on_pallet ?c ?p) (not (pallet_empty ?p)) (clear ?c))
  )

  (:action put_on_crate
    :parameters (?k - crane ?c - crate ?target - crate ?l - location)
    :precondition (and (crane_at ?k ?l) (holding ?k ?c) (crate_at ?target ?l) (clear ?target))
    :effect (and (not (holding ?k ?c)) (hoist_empty ?k) (crate_at ?c ?l) (on ?c ?target) (not (clear ?target)) (clear ?c))
  )

  (:action load_truck
    :parameters (?k - crane ?c - crate ?t - truck ?s - capacity_slot ?l - location)
    :precondition (and (crane_at ?k ?l) (truck_at ?t ?l) (holding ?k ?c) (slot_of ?s ?t) (slot_empty ?s))
    :effect (and (not (holding ?k ?c)) (hoist_empty ?k) (in ?c ?t ?s) (not (slot_empty ?s)) (not (clear ?c)))
  )

  (:action unload_truck
    :parameters (?k - crane ?c - crate ?t - truck ?s - capacity_slot ?l - location)
    :precondition (and (crane_at ?k ?l) (truck_at ?t ?l) (hoist_empty ?k) (in ?c ?t ?s))
    :effect (and (holding ?k ?c) (not (hoist_empty ?k)) (not (in ?c ?t ?s)) (slot_empty ?s) (not (clear ?c)))
  )

)