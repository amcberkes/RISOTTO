import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'hybrid_unidirectional_evaluation_results_0.3.csv'  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Create a seaborn multilevel bar chart with adjusted bar width
plt.figure(figsize=(14, 10))
bar_plot = sns.barplot(x='WFH Type', y='Cost', hue='Commute Distance', data=data, palette="rocket", ci=None)

# Additional customization
plt.ylabel('Average Cost', fontsize=16)
plt.xlabel('WFH Type', fontsize=16)
plt.xticks(rotation=0, fontsize=16)

# Increase the legend fontsize
plt.legend(title='Commute Distance', fontsize=16)

# Display the cost values above the bars without overlapping
for p in bar_plot.patches:
    x_pos = p.get_x() + p.get_width() / 2.
    y_pos = p.get_height() + 10  # Position the numbers slightly above the bars and increase offset to avoid overlap
    bar_plot.annotate(f'{int(p.get_height())}', 
                      (x_pos, y_pos), 
                      ha='center', va='bottom', 
                      fontsize=14)

# Display the plot
    plt.ylim(0, 25000)
plt.tight_layout()
plt.show()
