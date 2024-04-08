import seaborn as sns
import matplotlib.pyplot as plt

# Define the color palette
palette = "rocket"

# Define the file paths
file_paths = {
    "safe_bidirectional": "soc_values_safe_bidirectional.txt",
    "safe_unidirectional": "soc_values_safe_unidirectional.txt",
    "hybrid_bidirectional": "soc_values_hybrid_bidirectional.txt",
    "hybrid_unidirectional": "soc_values_hybrid_unidirectional.txt",
    "optimal_unidirectional": "soc_values_optimal_unidirectional.txt",
    "optimal_bidirectional": "soc_values_optimal_bidirectional.txt"
}

# Abbreviated policy names for x-axis labels
policy_labels = {
    "safe_bidirectional": "Safe Bid.",
    "safe_unidirectional": "Safe Unid.",
    "hybrid_bidirectional": "Hybrid Bid.",
    "hybrid_unidirectional": "Hybrid Unid.",
     "optimal_bidirectional": "Optimal Bid.",
    "optimal_unidirectional": "Optimal Unid."
   
}

# Initialize an empty list to store average SOC values
average_soc_values = []

# Calculate average SOC for each operation policy
for policy, file_path in file_paths.items():
    with open(file_path, "r") as file:
        soc_values = [float(line.strip()) for line in file]
        average_soc = sum(soc_values) / len(soc_values)
        average_soc_values.append(average_soc)

# Create a bar plot using Seaborn
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
ax = sns.barplot(x=list(policy_labels.values()), y=average_soc_values, palette=palette)
plt.xlabel("Operation Policy", fontsize=16)
plt.ylabel("Average SOC", fontsize=16)

# Display average SOC values above the bars with a bigger font size
for i, v in enumerate(average_soc_values):
    ax.text(i, v + 0.01, f"{v:.2f}", ha='center', va='bottom', fontsize=16)

plt.ylim(0, 40)

# Show the plot
plt.xticks(rotation=0, fontsize=14)  # Ensure horizontal x-axis labels
plt.tight_layout()
plt.show()
