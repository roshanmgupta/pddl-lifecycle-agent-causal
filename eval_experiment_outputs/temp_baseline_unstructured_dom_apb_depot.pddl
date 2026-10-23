(define (domain depot)
  (:requirements :strips :typing)
  (:types
    depot distributor - Place
    truck hoist - Locatable
    pallet crate - Surface
  )
  (:predicates
    (at ?obj - Locatable ?place - Place)
    (clear ?obj - Locatable)
    (available ?hoist - Hoist)
    (lifting ?hoist - Hoist ?crate - Crate)
    (on ?crate - Crate ?surface - Surface)
  )
  
  (:action drive
    :parameters (?truck - Truck ?from - Place ?to - Place)
    :precondition (at ?truck ?from)
    :effect (and
      (at ?truck ?to)
      (not (at ?truck ?from))
    )
  )

  (:action lift
    :parameters (?hoist - Hoist ?crate - Crate ?surface - Surface ?place - Place)
    :precondition (and
      (at ?hoist ?place)
      (available ?hoist)
      (at ?crate ?place)
      (on ?crate ?surface)
      (clear ?crate)
    )
    :effect (and
      (lifting ?hoist ?crate)
      (clear ?surface)
      (not (at ?crate ?place))
      (not (clear ?crate))
      (not (available ?hoist))
      (not (on ?crate ?surface))
    )
  )

  (:action drop
    :parameters (?hoist - Hoist ?crate - Crate ?surface - Surface ?place - Place)
    :precondition (and
      (at ?hoist ?place)
      (at ?surface ?place)
      (clear ?surface)
      (lifting ?hoist ?crate)
    )
    :effect (and
      (available ?hoist)
      (at ?crate ?place)
      (clear ?crate)
      (on ?crate ?surface)
      (not (lifting ?hoist ?crate))
      (not (clear ?surface))
    )
  )

  (:action load
    :parameters (?hoist - Hoist ?crate - Crate ?truck - Truck ?place - Place)
    :precondition (and
      (at ?hoist ?place)
      (at ?truck ?place)
      (lifting ?hoist ?crate)
    )
    :effect (and
      (in ?crate ?truck)
      (available ?hoist)
      (not (lifting ?hoist ?crate))
    )
  )

  (:action unload
    :parameters (?hoist - Hoist ?crate - Crate ?truck - Truck ?place - Place)
    :precondition (and
      (at ?hoist ?place)
      (at ?truck ?place)
      (available ?hoist)
      (in ?crate ?truck)
    )
    :effect (and
      (lifting ?hoist ?crate)
      (not (in ?crate ?truck))
      (not (available ?hoist))
    )
  )
)