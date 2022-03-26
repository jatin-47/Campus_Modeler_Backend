for i in 1 2 3 4 5 6 7 8 9 10
do
    echo "Running experiment number $i"
    python run_simulation.py -SimName Sim_"$i"
done
