;; Peg Solitaire sequential domain

(define (domain pegsolitaire-sequential)
    (:requirements :typing)
    (:types location - object)
    (:predicates
    (specialized_mode_enabled)
        (IN-LINE ?x ?y ?z - location)
        (occupied ?l - location)
        (free ?l - location)
        (move-ended)
        (last-visited ?l - location)
    )

    (:action jump-new-move
     :parameters (?from - location ?over - location ?to - location)
     :precondition (and 
                       (move-ended)
                       (IN-LINE ?from ?over ?to)
                       (occupied ?from)
                       (occupied ?over)
                       (free ?to)
                   )
     :effect (and
                 (not (move-ended))
                 (not (occupied ?from))
                 (not (occupied ?over))
                 (not (free ?to))
                 (free ?from)
                 (free ?over)
                 (occupied ?to)
                 (last-visited ?to)
             )
    )

    (:action jump-continue-move
     :parameters (?from - location ?over - location ?to - location)
     :precondition (and 
                       (last-visited ?from)
                       (IN-LINE ?from ?over ?to)
                       (occupied ?from)
                       (occupied ?over)
                       (free ?to)
                   )
     :effect (and
                 (not (occupied ?from))
                 (not (occupied ?over))
                 (not (free ?to))
                 (free ?from)
                 (free ?over)
                 (occupied ?to)
                 (not (last-visited ?from))
                 (last-visited ?to)
             )
    )

    (:action end-move
     :parameters (?loc - location)
     :precondition (and (specialized_mode_enabled) last-visited ?loc)
     :effect (and
                 (move-ended)
                 (not (last-visited ?loc))
             )
    )
)
