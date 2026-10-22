(define (problem instance-1)
  (:domain data-network18)

  (:objects
    data-0-3 - data
    data-0-5 - data
    data-1-2 - data
    data-1-4 - data
    data-2-1 - data
    script1 - script
    script2 - script
    script3 - script
    script4 - script
    script5 - script
    script6 - script
    script7 - script
    script8 - script
    script9 - script
    script10 - script
    server1 - server
    server2 - server
    server3 - server
    number0 - numbers
    number1 - numbers
    number2 - numbers
    number3 - numbers
    number4 - numbers
    number5 - numbers
    number6 - numbers
    number7 - numbers
    number8 - numbers
    number9 - numbers
    number10 - numbers
    number11 - numbers
    number12 - numbers
    number13 - numbers
    number14 - numbers
    number15 - numbers
    number16 - numbers
  )

  (:init
    (script-takes-inputs script1 data-0-3 data-0-5)
    (script-takes-inputs script2 data-0-5 data-0-3)
    (script-takes-inputs script3 data-1-4 data-0-5)
    (script-takes-inputs script4 data-0-3 data-0-5)
    (script-takes-inputs script5 data-1-2 data-0-5)
    (script-takes-inputs script6 data-1-2 data-0-3)
    (script-takes-inputs script7 data-0-5 data-0-3)
    (script-takes-inputs script8 data-1-4 data-1-2)
    (script-takes-inputs script9 data-0-3 data-0-5)
    (script-takes-inputs script10 data-1-2 data-1-4)
    (script-produces-output script1 data-1-4)
    (script-produces-output script2 data-1-2)
    (script-produces-output script3 data-2-1)
    (script-produces-output script4 data-1-4)
    (script-produces-output script5 data-2-1)
    (script-produces-output script6 data-2-1)
    (script-produces-output script7 data-1-2)
    (script-produces-output script8 data-2-1)
    (script-produces-output script9 data-1-4)
    (script-produces-output script10 data-2-1)
    (connected server1 server2)
    (connected server2 server1)
    (connected server1 server3)
    (connected server3 server1)
    (data-size data-0-3 number4)
    (data-size data-0-5 number5)
    (data-size data-1-2 number4)
    (data-size data-1-4 number1)
    (data-size data-2-1 number4)
    (capacity server1 number16)
    (capacity server2 number8)
    (capacity server3 number8)
    (sum number0 number1 number1)
    (sum number0 number4 number4)
    (sum number0 number5 number5)
    (sum number1 number1 number2)
    (sum number1 number4 number5)
    (sum number1 number5 number6)
    (sum number2 number1 number3)
    (sum number2 number4 number6)
    (sum number2 number5 number7)
    (sum number3 number1 number4)
    (sum number3 number4 number7)
    (sum number3 number5 number8)
    (sum number4 number1 number5)
    (sum number4 number4 number8)
    (sum number4 number5 number9)
    (sum number5 number1 number6)
    (sum number5 number4 number9)
    (sum number5 number5 number10)
    (sum number6 number1 number7)
    (sum number6 number4 number10)
    (sum number6 number5 number11)
    (sum number7 number1 number8)
    (sum number7 number4 number11)
    (sum number7 number5 number12)
    (sum number8 number1 number9)
    (sum number8 number4 number12)
    (sum number8 number5 number13)
    (sum number9 number1 number10)
    (sum number9 number4 number13)
    (sum number9 number5 number14)
    (sum number10 number1 number11)
    (sum number10 number4 number14)
    (sum number10 number5 number15)
    (sum number11 number1 number12)
    (sum number11 number4 number15)
    (sum number11 number5 number16)
    (sum number12 number1 number13)
    (sum number12 number4 number16)
    (sum number13 number1 number14)
    (sum number14 number1 number15)
    (sum number15 number1 number16)
    (leq number1 number8)
    (leq number1 number16)
    (leq number2 number8)
    (leq number2 number16)
    (leq number3 number8)
    (leq number3 number16)
    (leq number4 number8)
    (leq number4 number16)
    (leq number5 number8)
    (leq number5 number16)
    (leq number6 number8)
    (leq number6 number16)
    (leq number7 number8)
    (leq number7 number16)
    (leq number8 number8)
    (leq number8 number16)
    (leq number9 number16)
    (leq number10 number16)
    (leq number11 number16)
    (leq number12 number16)
    (leq number13 number16)
    (leq number14 number16)
    (leq number15 number16)
    (leq number16 number16)
    (saved data-0-3 server3)
    (saved data-0-5 server1)
    (usage server1 number0)
    (usage server2 number0)
    (usage server3 number0)
  )

  (:goal (and (saved data-2-1 server2)))
)