import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde

def plot_soc_cdf(file_paths):
    # Set seaborn style and color palette
    sns.set(style="whitegrid", palette="rocket")

    # Plot the CDFs for each operation policy
    plt.figure(figsize=(12, 8))
    for policy, file_path in file_paths.items():
        with open(file_path, 'r') as file:
            soc_values = np.array([float(line.strip()) for line in file])
            kde = gaussian_kde(soc_values)
            soc_range = np.linspace(28, 34, 1000)
            pdf_values = kde(soc_range)
            cdf_values = np.cumsum(pdf_values) / sum(pdf_values)  # Compute CDF
            plt.plot(soc_range, cdf_values, label=f'CDF of {policy.replace("_", " ").title()}')

    # Customize the plot
    plt.xlabel('SOC at Departure')
    plt.ylabel('Cumulative Probability')
    plt.title('Cumulative Distribution Function of SOC at Departure for Different Policies')
    plt.legend()

    # Annotate max_soc
    plt.axvline(x=32.0, color='gray', linestyle='--')
    plt.text(32.0, plt.ylim()[1], 'max_soc', ha='left', va='bottom', color='gray')

    # Set the x-axis limits to focus on SOC values from 28 to 34
    plt.xlim(28, 34)

    # Show the plot
    plt.show()

# Define the file names for each operation policy
file_paths = {
    "safe_bidirectional": "soc_values_safe_bidirectional.txt",
    "safe_unidirectional": "soc_values_safe_unidirectional.txt",
    "hybrid_bidirectional": "soc_values_hybrid_bidirectional.txt",
    "hybrid_unidirectional": "soc_values_hybrid_unidirectional.txt",
    "optimal_unidirectional": "soc_values_optimal_unidirectional.txt",
    "optimal_bidirectional": "soc_values_optimal_bidirectional.txt"
}

# Call the function with the file paths
plot_soc_cdf(file_paths)
