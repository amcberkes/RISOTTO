import pandas as pd

# Load the CSV data using semicolon as the delimiter and skip the appropriate number of rows to reach the actual data
# pvwattshourly is weymouth with 4kw solar
#data = pd.read_csv('pvwatts_hourly_2.csv', delimiter=';', skiprows=31)
data = pd.read_csv('pvwatts_hourly_2.csv')
print(data)

# Extract the 'AC System Output (W)' column and convert values from watts to kilowatts
ac_output_kw = data['AC System Output (W)'] / 1000

# Path to the output file
output_file_path = 'Weymouth_pv_2.txt'

# Write to a new text file with each value on a new line
with open(output_file_path, 'w') as file:
    for value in ac_output_kw:
        file.write(f"{value}\n")

# Optionally, print or check how many lines are written to ensure correctness
print(f"Total lines written: {len(ac_output_kw)}")
