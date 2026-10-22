(define (problem iss_daily_schedule_problem)
  (:domain iss_schedule)

  (:objects
    astro1 - astronaut
    astro2 - astronaut
    day1 - day
    day2 - day
    treadmill - exercise_station
    rpcm_task1 - maintenance_task
    filter_task1 - maintenance_task
  )

  (:init
    (current_day astro1 day1)
    (current_day astro2 day1)
    (next_day day1 day2)
    (station_available treadmill)
    (task_assigned rpcm_task1 astro1)
    (is_rpcm_task rpcm_task1)
    (task_assigned filter_task1 astro2)
    (is_filter_task filter_task1)
  )

  (:goal (and (done_sleep astro1 day1) (done_sleep astro2 day1) (task_completed rpcm_task1) (task_completed filter_task1)))
)