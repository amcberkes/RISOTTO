import pandas as pd

# Load the data into a pandas DataFrame
data = pd.read_csv('evaluation_results_20_interm_0.2_second.csv')

# Group by Operation Policy and WFH Type, and calculate the average values
avg_data = data.groupby(['Operation Policy', 'WFH Type']).mean().reset_index()

# Select only the relevant columns
avg_data = avg_data[['Operation Policy', 'WFH Type', 'Battery', 'PV', 'Cost']]

# Print the averaged results
print(avg_data)

# Optionally, save the averaged results to a CSV file
avg_data.to_csv("average_results_20_0.2.csv", index=False)
