(define (problem instance-1.pddl)
  (:domain woodworking08)
  (:objects
    grinder0 - grinder
    glazer0 - glazer
    immersion-varnisher0 - immersion-varnisher
    planer0 - planer
    highspeed-saw0 - highspeed-saw
    spray-varnisher0 - spray-varnisher
    saw0 - saw
    green mauve - acolour
    cherry beech - awood
    p0 p1 p2 - part
    b0 b1 - board
    s0 s1 s2 s3 - aboardsize
  )
  
  (:init
    (successor s0 s1)
    (successor s1 s2)
    (successor s2 s3)
    (has-color glazer0 mauve)
    (has-color glazer0 green)
    (has-color immersion-varnisher0 mauve)
    (is-empty highspeed-saw0)
    (has-color spray-varnisher0 mauve)
    (unused p0)
    (goal-size p0 medium)
    (unused p1)
    (goal-size p1 medium)
    (available p2)
    (has-color p2 natural)
    (has-wood p2 beech)
    (has-surface p2 verysmooth)
    (undergoing-treatment p2 colourfragments)
    (goal-size p2 small)
    (has-wood b0 beech)
    (has-surface b0 rough)
    (has-color b0 natural)
    (available b0)
    (has-wood b1 cherry)
    (has-surface b1 rough)
    (has-color b1 natural)
    (available b1)
  )
  
  (:goal
    (and
      (available p0)
      (has-color p0 mauve)
      (has-wood p0 beech)
      (has-surface p0 verysmooth)
      (undergoing-treatment p0 varnished)
      (available p1)
      (has-color p1 green)
      (has-wood p1 cherry)
      (has-surface p1 smooth)
      (undergoing-treatment p1 glazed)
      (available p2)
      (has-color p2 mauve)
      (has-wood p2 beech)
    )
  )
)