import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'averaged_evaluation_results_10_0.5_new.csv'  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Map operation policy labels using policy_labels dictionary
policy_labels = {
    "safe_bidirectional": "N-B",
    "safe_unidirectional": "N-U",
    "hybrid_bidirectional": "SG-B",
    "hybrid_unidirectional": "SG-U",
    "optimal_bidirectional": "SO-B",
    "optimal_unidirectional": "SO-U"
}

data['Operation Policy'] = data['Operation Policy'].map(policy_labels)

# Create a seaborn multilevel bar chart with adjusted bar width
plt.figure(figsize=(12, 8))
bar_plot = sns.barplot(x='Operation Policy', y='Battery', hue='WFH Type', data=data, palette="rocket", ci=None)
sns.color_palette("flare", as_cmap=True)

# Additional customization
plt.ylabel('Average Battery Size', fontsize=16)
plt.xlabel('Operation Policy', fontsize=16)
plt.xticks(rotation=0, fontsize=16)

# Increase the legend fontsize
plt.legend(title='WFH Type', fontsize=16)

# Display the battery size values right above the bars with one decimal number
for p in bar_plot.patches:
    x_pos = p.get_x() + p.get_width() / 2.
    y_pos = p.get_height()  # Position the numbers above the bars
    value = round(p.get_height(), 1)
    bar_plot.annotate(f'{value}', 
                      (x_pos, y_pos), 
                      ha='center', va='bottom', 
                      fontsize=16)

# Display the plot
plt.tight_layout()
plt.xticks(rotation=0, fontsize=16)  # Ensure horizontal x-axis labels

plt.show()
