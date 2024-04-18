import os
import numpy as np
import matplotlib.pyplot as plt

# List of directories to analyze
directories = ['Terraced_100', 'Semi_Detached_100', 'Detached_100']

def process_directory(directory):
    a_loads = []
    d_loads = []

    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as f:
                loads = np.array([float(line.strip()) for line in f.readlines()])
                if filename.startswith('A_'):
                    a_loads.append(loads)
                elif filename.startswith('D_'):
                    d_loads.append(loads)

    # Aggregate the data
    if a_loads:
        a_total_load = np.sum(a_loads, axis=0)
        a_annual_average = np.sum(a_total_load) / 59
        print(f"Total Annual Average Load for A in {directory}: {a_annual_average}")
        a_daily_average = np.mean(a_loads, axis=0)
    if d_loads:
        d_total_load = np.sum(d_loads, axis=0)
        d_annual_average = np.sum(d_total_load) / 41
        print(f"Total Annual Average Load for D in {directory}: {d_annual_average}")
        d_daily_average = np.mean(d_loads, axis=0)

    # Plotting
    plt.figure(figsize=(10, 5))
    if a_loads:
        plt.plot(range(24), a_daily_average[:24], label=f'Average Daily Load Curve A - {directory}')
    if d_loads:
        plt.plot(range(24), d_daily_average[:24], label=f'Average Daily Load Curve D - {directory}')
    plt.title(f'Average Daily Load Curve in {directory}')
    plt.xlabel('Hour of Day')
    plt.ylabel('Load (kWh)')
    plt.xticks(range(24))
    plt.legend()
    plt.grid(True)
    plt.show()

for directory in directories:
    process_directory(directory)
