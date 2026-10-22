(define (domain ged14)
  (:requirements :strips :typing)

  (:types
    gene object - object
  )

  (:predicates
    (normal ?g - gene)
    (inverted ?g - gene)
    (present ?g - gene)
    (clockwise ?g1 - gene ?g2 - gene)
    (idle)
    (being_cut)
    (has_been_cut)
    (splicing_happening)
    (performing_inverse_splicing)
    (finished)
    (at_cut_point_1 ?g - gene)
    (at_cut_point_2 ?g - gene)
    (at_splice_point_1 ?g - gene)
    (at_splice_point_2 ?g - gene)
    (last_in_sequence ?g - gene)
    (first_in_sequence ?g - gene)
    (next_in_sequence_after ?g1 - gene ?g2 - gene)
    (splice_next ?g1 - gene ?g2 - gene)
    (splicing_last_one)
    (performing_inverse_splice_next ?g1 - gene ?g2 - gene)
    (performing_inverse_splicing_last)
    (at_last_cut_point ?g - gene)
  )

  (:action begin_cutting
    :parameters (?a - gene ?b - gene)
    :precondition (and (idle) (clockwise ?a ?b) (not (= ?a ?b)))
    :effect (and (being_cut) (at_cut_point_1 ?a) (at_last_cut_point ?a) (first_in_sequence ?b) (last_in_sequence ?b) (not (idle)) (not (clockwise ?a ?b)))
  )

  (:action continue_cutting
    :parameters (?a - gene ?b - gene)
    :precondition (and (being_cut) (last_in_sequence ?a) (clockwise ?a ?b) (not (= ?a ?b)))
    :effect (and (next_in_sequence_after ?a ?b) (last_in_sequence ?b) (not (clockwise ?a ?b)) (not (last_in_sequence ?a)))
  )

  (:action end_cut
    :parameters (?a - gene ?b - gene)
    :precondition (and (being_cut) (last_in_sequence ?a) (clockwise ?a ?b) (not (= ?a ?b)))
    :effect (and (at_cut_point_2 ?b) (not (clockwise ?a ?b)))
  )

  (:action end_cut_at_points
    :parameters (?a - gene ?b - gene)
    :precondition (and (being_cut) (at_cut_point_1 ?a) (at_cut_point_2 ?b))
    :effect (and (has_been_cut) (clockwise ?a ?b) (not (being_cut)) (not (at_cut_point_1 ?a)) (not (at_cut_point_2 ?b)))
  )

  (:action begin_transpose_splice
    :parameters (?a - gene ?b - gene)
    :precondition (and (has_been_cut) (clockwise ?a ?b) (not (= ?a ?b)))
    :effect (and (splicing_happening) (at_splice_point_1 ?a) (at_splice_point_2 ?b) (not (has_been_cut)) (not (clockwise ?a ?b)))
  )

  (:action continue_splice_1
    :parameters (?a - gene ?b - gene)
    :precondition (and (splicing_happening) (first_in_sequence ?a) (next_in_sequence_after ?a ?b))
    :effect (and (first_in_sequence ?b) (splice_next ?a ?b) (not (first_in_sequence ?a)) (not (next_in_sequence_after ?a ?b)) (not (splicing_happening)))
  )

  (:action continue_splice_2
    :parameters (?a - gene ?b - gene)
    :precondition (and (splice_next ?a ?b) (at_splice_point_1 ?b))
    :effect (and (clockwise ?b ?a) (at_splice_point_1 ?a) (splicing_happening) (not (at_splice_point_1 ?b)) (not (splice_next ?a ?b)))
  )

  (:action end_splice_1
    :parameters (?a - gene ?b - gene)
    :precondition (and (splicing_happening) (at_splice_point_1 ?b) (first_in_sequence ?a) (last_in_sequence ?a))
    :effect (and (splicing_last_one) (clockwise ?b ?a) (at_splice_point_1 ?a) (not (splicing_happening)) (not (first_in_sequence ?a)) (not (last_in_sequence ?a)) (not (at_splice_point_1 ?b)))
  )

  (:action end_splice_2
    :parameters (?a - gene ?b - gene)
    :precondition (and (splicing_last_one) (at_splice_point_1 ?a) (at_splice_point_2 ?b))
    :effect (and (finished) (clockwise ?a ?b) (not (splicing_last_one)) (not (at_splice_point_1 ?a)) (not (at_splice_point_2 ?b)))
  )

  (:action begin_transverse_splice
    :parameters (?a - gene ?b - gene)
    :precondition (and (has_been_cut) (clockwise ?a ?b) (not (= ?a ?b)))
    :effect (and (performing_inverse_splicing) (at_splice_point_1 ?a) (at_splice_point_2 ?b) (not (has_been_cut)) (not (clockwise ?a ?b)))
  )

  (:action begin_inverse_splice
    :parameters (?a - gene ?b - gene)
    :precondition (and (has_been_cut) (clockwise ?a ?b) (at_last_cut_point ?a) (not (= ?a ?b)))
    :effect (and (performing_inverse_splicing) (at_splice_point_1 ?a) (at_splice_point_2 ?b) (not (has_been_cut)) (not (clockwise ?a ?b)))
  )

  (:action begin_inverse_splice_special_case
    :parameters (?a - gene)
    :precondition (and (has_been_cut) (clockwise ?a ?a) (at_last_cut_point ?a))
    :effect (and (performing_inverse_splicing) (at_splice_point_1 ?a) (at_splice_point_2 ?a) (not (has_been_cut)) (not (clockwise ?a ?a)))
  )

  (:action continue_inverse_splice_1a
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splicing) (normal ?a) (last_in_sequence ?a) (next_in_sequence_after ?b ?a))
    :effect (and (last_in_sequence ?b) (performing_inverse_splice_next ?a ?a) (inverted ?a) (not (last_in_sequence ?a)) (not (next_in_sequence_after ?b ?a)) (not (normal ?a)) (not (performing_inverse_splicing)))
  )

  (:action continue_inverse_splice_1b
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splicing) (inverted ?a) (last_in_sequence ?a) (next_in_sequence_after ?b ?a))
    :effect (and (last_in_sequence ?b) (performing_inverse_splice_next ?a ?a) (normal ?a) (not (last_in_sequence ?a)) (not (next_in_sequence_after ?b ?a)) (not (inverted ?a)) (not (performing_inverse_splicing)))
  )

  (:action continue_inverse_splice_2
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splice_next ?a ?b) (at_splice_point_1 ?b))
    :effect (and (performing_inverse_splicing) (clockwise ?b ?a) (at_splice_point_1 ?a) (not (performing_inverse_splice_next ?a ?b)) (not (at_splice_point_1 ?b)))
  )

  (:action end_inverse_splice_1a
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splicing) (normal ?a) (at_splice_point_1 ?b) (first_in_sequence ?a) (last_in_sequence ?a))
    :effect (and (performing_inverse_splicing_last) (clockwise ?b ?a) (at_splice_point_1 ?a) (inverted ?a) (not (performing_inverse_splicing)) (not (at_splice_point_1 ?b)) (not (first_in_sequence ?a)) (not (last_in_sequence ?a)) (not (normal ?a)))
  )

  (:action end_inverse_splice_1b
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splicing) (inverted ?a) (at_splice_point_1 ?b) (first_in_sequence ?a) (last_in_sequence ?a))
    :effect (and (performing_inverse_splicing_last) (clockwise ?b ?a) (at_splice_point_1 ?a) (normal ?a) (not (performing_inverse_splicing)) (not (at_splice_point_1 ?b)) (not (first_in_sequence ?a)) (not (last_in_sequence ?a)) (not (inverted ?a)))
  )

  (:action end_inverse_splice_2
    :parameters (?a - gene ?b - gene)
    :precondition (and (performing_inverse_splicing_last) (at_splice_point_1 ?a) (at_splice_point_2 ?b))
    :effect (and (finished) (clockwise ?a ?b) (not (performing_inverse_splicing_last)) (not (at_splice_point_1 ?a)) (not (at_splice_point_2 ?b)))
  )

  (:action invert_single_gene_a
    :parameters (?a - gene)
    :precondition (and (idle) (normal ?a))
    :effect (and (inverted ?a) (not (normal ?a)))
  )

  (:action invert_single_gene_b
    :parameters (?a - gene)
    :precondition (and (idle) (inverted ?a))
    :effect (and (normal ?a) (not (inverted ?a)))
  )

  (:action reset_1
    :parameters (?a - gene)
    :precondition (and (finished) (at_last_cut_point ?a))
    :effect (and (idle) (not (at_last_cut_point ?a)) (not (finished)))
  )

)