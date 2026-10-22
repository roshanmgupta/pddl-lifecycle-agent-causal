(define (domain barman11-bfs)
  (:requirements :strips :typing)
  (:types
    hand level beverage dispenser container - object
    ingredient cocktail - beverage
    shot shaker - container
  )
  (:predicates
    (on-table ?x - container)
    (holding ?h - hand ?c - container)
    (empty ?h - hand)
    (dispenses ?d - dispenser ?i - ingredient)
    (clean ?c - container)
    (used ?c - container ?b - beverage)
    (contains ?c - container ?b - beverage)
    (empty ?c - container)
    (shaken ?s - shaker)
    (unshaken ?s - shaker)
    (at ?s - shaker ?l - level)
    (next ?l1 ?l2 - level)
    (part-of ?c - cocktail ?i - ingredient)
    (another-part-of ?c - cocktail ?i - ingredient)
  )
  (:action grasp
    :parameters (?b - container ?a - hand)
    :precondition (and (on-table ?b) (empty ?a))
    :effect (and (not (on-table ?b)) (not (empty ?a)) (holding ?a ?b))
  )
  (:action leave
    :parameters (?b - container ?a - hand)
    :precondition (holding ?a ?b)
    :effect (and (empty ?a) (on-table ?b) (not (holding ?a ?b)))
  )
  (:action fill
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (dispenses ?e ?b) (empty ?a) (clean ?a))
    :effect (and (contains ?a ?b) (used ?a ?b) (not (empty ?a)) (not (clean ?a)))
  )
  (:action refill
    :parameters (?a - shot ?b - ingredient ?e - dispenser ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (dispenses ?e ?b) (empty ?a) (used ?a ?b))
    :effect (and (contains ?a ?b) (not (empty ?a)))
  )
  (:action empty-shot
    :parameters (?b - shot ?c - beverage ?a - hand)
    :precondition (and (holding ?a ?b) (contains ?b ?c))
    :effect (and (empty ?b) (not (contains ?b ?c)))
  )
  (:action clean-shot
    :parameters (?a - shot ?b - beverage ?c - hand ?d - hand)
    :precondition (and (holding ?c ?a) (empty ?d) (empty ?a) (used ?a ?b))
    :effect (and (clean ?a) (not (used ?a ?b)))
  )
  (:action pour-clean-shaker
    :parameters (?b - ingredient ?a - shot ?c - shaker ?d - hand ?e ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (empty ?c) (clean ?c) (at ?c ?e) (next ?e ?f))
    :effect (and (empty ?a) (contains ?c ?b) (unshaken ?c) (at ?c ?f) (not (contains ?a ?b)) (not (empty ?c)) (not (clean ?c)) (not (at ?c ?e)))
  )
  (:action pour-used-shaker
    :parameters (?b - ingredient ?a - shot ?c - shaker ?d - hand ?e ?f - level)
    :precondition (and (holding ?d ?a) (contains ?a ?b) (unshaken ?c) (at ?c ?e) (next ?e ?f))
    :effect (and (contains ?c ?b) (empty ?a) (at ?c ?f) (not (contains ?a ?b)) (not (at ?c ?e)))
  )
  (:action empty-shaker
    :parameters (?b - shaker ?c - cocktail ?a - hand ?d ?e - level)
    :precondition (and (holding ?a ?b) (contains ?b ?c) (shaken ?b) (at ?b ?d) (at ?b ?e))
    :effect (and (at ?b ?e) (empty ?b) (not (shaken ?b)) (not (at ?b ?d)) (not (contains ?b ?c)))
  )
  (:action clean-shaker
    :parameters (?c - shaker ?a - hand ?b - hand)
    :precondition (and (holding ?a ?c) (empty ?b) (empty ?c))
    :effect (and (clean ?c))
  )
  (:action shake
    :parameters (?a - cocktail ?d - shaker ?e - hand ?f - hand ?b ?c - ingredient)
    :precondition (and (holding ?e ?d) (empty ?f) (contains ?d ?b) (contains ?d ?c) (part-of ?a ?b) (another-part-of ?a ?c) (unshaken ?d))
    :effect (and (shaken ?d) (contains ?d ?a) (not (unshaken ?d)) (not (contains ?d ?b)) (not (contains ?d ?c)))
  )
  (:action pour-shaker-to-shot
    :parameters (?a - beverage ?d - shaker ?c - hand ?b - shot ?e ?f - level)
    :precondition (and (holding ?c ?d) (shaken ?d) (empty ?b) (clean ?b) (contains ?d ?a) (at ?d ?e) (next ?e ?f))
    :effect (and (contains ?b ?a) (at ?d ?f) (not (clean ?b)) (not (empty ?b)) (not (at ?d ?e)))
  )
)