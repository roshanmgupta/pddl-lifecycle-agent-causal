(define (domain iss_schedule)
  (:requirements :strips :typing)

  (:types
    astronaut day exercise_station maintenance_task - object
  )

  (:predicates
    (current_day ?a - astronaut ?d - day)
    (next_day ?d1 - day ?d2 - day)
    (done_post_sleep ?a - astronaut ?d - day)
    (done_meal_1 ?a - astronaut ?d - day)
    (done_planning ?a - astronaut ?d - day)
    (done_meal_2 ?a - astronaut ?d - day)
    (done_exercise ?a - astronaut ?d - day)
    (done_meal_3 ?a - astronaut ?d - day)
    (done_pre_sleep ?a - astronaut ?d - day)
    (done_sleep ?a - astronaut ?d - day)
    (station_available ?e - exercise_station)
    (task_assigned ?t - maintenance_task ?a - astronaut)
    (is_rpcm_task ?t - maintenance_task)
    (is_filter_task ?t - maintenance_task)
    (sleep_station_dismantled ?t - maintenance_task)
    (thermal_loop_reconfigured ?t - maintenance_task)
    (hardware_swapped ?t - maintenance_task)
    (task_completed ?t - maintenance_task)
  )

  (:action perform_post_sleep
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (not (done_post_sleep ?a ?d)))
    :effect (done_post_sleep ?a ?d)
  )

  (:action eat_meal_1
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (done_post_sleep ?a ?d) (not (done_meal_1 ?a ?d)))
    :effect (done_meal_1 ?a ?d)
  )

  (:action attend_planning_conference
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (done_meal_1 ?a ?d) (not (done_planning ?a ?d)))
    :effect (done_planning ?a ?d)
  )

  (:action eat_meal_2
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (done_planning ?a ?d) (not (done_meal_2 ?a ?d)))
    :effect (done_meal_2 ?a ?d)
  )

  (:action exercise
    :parameters (?a - astronaut ?e - exercise_station ?d - day)
    :precondition (and (current_day ?a ?d) (done_meal_2 ?a ?d) (station_available ?e) (not (done_exercise ?a ?d)))
    :effect (done_exercise ?a ?d)
  )

  (:action eat_meal_3
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (done_exercise ?a ?d) (not (done_meal_3 ?a ?d)))
    :effect (done_meal_3 ?a ?d)
  )

  (:action perform_pre_sleep
    :parameters (?a - astronaut ?d - day)
    :precondition (and (current_day ?a ?d) (done_meal_3 ?a ?d) (not (done_pre_sleep ?a ?d)))
    :effect (done_pre_sleep ?a ?d)
  )

  (:action sleep_uninterrupted
    :parameters (?a - astronaut ?d - day ?next_d - day)
    :precondition (and (current_day ?a ?d) (done_pre_sleep ?a ?d) (next_day ?d ?next_d) (not (done_sleep ?a ?d)))
    :effect (and (done_sleep ?a ?d) (not (current_day ?a ?d)) (current_day ?a ?next_d))
  )

  (:action rpcm_dismantle_sleep_station
    :parameters (?a - astronaut ?t - maintenance_task)
    :precondition (and (task_assigned ?t ?a) (is_rpcm_task ?t) (not (sleep_station_dismantled ?t)))
    :effect (sleep_station_dismantled ?t)
  )

  (:action rpcm_reconfigure_thermal_loop
    :parameters (?a - astronaut ?t - maintenance_task)
    :precondition (and (task_assigned ?t ?a) (is_rpcm_task ?t) (sleep_station_dismantled ?t) (not (thermal_loop_reconfigured ?t)))
    :effect (thermal_loop_reconfigured ?t)
  )

  (:action rpcm_swap_hardware
    :parameters (?a - astronaut ?t - maintenance_task)
    :precondition (and (task_assigned ?t ?a) (is_rpcm_task ?t) (thermal_loop_reconfigured ?t) (not (hardware_swapped ?t)))
    :effect (hardware_swapped ?t)
  )

  (:action rpcm_reassemble_sleep_station
    :parameters (?a - astronaut ?t - maintenance_task)
    :precondition (and (task_assigned ?t ?a) (is_rpcm_task ?t) (hardware_swapped ?t) (not (task_completed ?t)))
    :effect (task_completed ?t)
  )

  (:action change_filter
    :parameters (?a - astronaut ?t - maintenance_task)
    :precondition (and (task_assigned ?t ?a) (is_filter_task ?t) (not (task_completed ?t)))
    :effect (task_completed ?t)
  )

)