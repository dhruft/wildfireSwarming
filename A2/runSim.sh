#!/bin/bash

iters=30
minFuel=4000
maxFuel=15000

for ((i = 0; i <= iters; i++)); do
    # Calculate the new value for the variable in vars.py
    fuel=$((minFuel + (i * (maxFuel - minFuel) / iters)))

    # Replace the desired variable in vars.py with the new value
    sed -i "s/startFuel = .*/startFuel = $fuel/" vars.py

    # Run main.py
    python3 main.py
done

# for i in {1..iters}
#     # Define the new value for the variable in vars.py
#     fuel = minFuel+i*(maxFuel-minFuel)/iters

#     # Replace the desired variable in vars.py with the new value
#     sed -i "s/startFuel = .*/startFuel = '$fuel'/" vars.py

#     # Run main.py
#     python main.py
# done