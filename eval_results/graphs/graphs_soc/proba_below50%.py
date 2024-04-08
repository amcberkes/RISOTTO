import numpy as np

# Define the file paths
file_paths = {
    "safe_bidirectional": "soc_values_safe_bidirectional.txt",
    "safe_unidirectional": "soc_values_safe_unidirectional.txt",
    "hybrid_bidirectional": "soc_values_hybrid_bidirectional.txt",
    "hybrid_unidirectional": "soc_values_hybrid_unidirectional.txt",
    "optimal_unidirectional": "soc_values_optimal_unidirectional.txt",
    "optimal_bidirectional": "soc_values_optimal_bidirectional.txt"
}

# Define thresholds
threshold_20 = 20  # kWh
threshold_16 = 16  # kWh

# Initialize dictionaries to store probabilities
prob_below_20 = {}
prob_below_16 = {}

# Calculate probabilities for each operation policy
for policy, file_path in file_paths.items():
    with open(file_path, "r") as file:
        soc_values = [float(line.strip()) for line in file]
        
        # Calculate the probability that the average SOC is below 20 kWh
        prob_below_20[policy] = np.mean(np.array(soc_values) < threshold_20)
        
        # Calculate the probability that the average SOC is below 16 kWh
        prob_below_16[policy] = np.mean(np.array(soc_values) < threshold_16)

# Print the probabilities
print("Probabilities that the average SOC is below 20 kWh:")
for policy, probability in prob_below_20.items():
    print(f"{policy}: {probability:.2%}")

print("\nProbabilities that the average SOC is below 16 kWh:")
for policy, probability in prob_below_16.items():
    print(f"{policy}: {probability:.2%}")
