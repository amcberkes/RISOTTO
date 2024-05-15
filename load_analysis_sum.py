import os
import numpy as np

# List of directories to analyze
directories = ['Terraced_100', 'Semi_Detached_100', 'Detached_100']

def process_directory(directory):
    total_loads = []

    # Traverse through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as f:
                loads = np.array([float(line.strip()) for line in f.readlines()])
                total_loads.append(loads)

    # Aggregate the data
    if total_loads:
        total_load = np.sum(total_loads, axis=0)
        annual_average = np.sum(total_load) / len(total_loads)  # Average over the number of files
        return annual_average
    return 0  # Return 0 if no loads were found

# Process each directory and store results
results = {}
for directory in directories:
    annual_average = process_directory(directory)
    results[directory] = annual_average

# Output the results
for category, load in results.items():
    print(f"Total Average Yearly Load for {category.split('_')[0]} Houses: {load:.2f} kWh")
