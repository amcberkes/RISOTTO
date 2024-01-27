import subprocess
import pandas as pd
import re

def extract_load_number(filename):
    match = re.search(r'load_(\d+).txt', filename)
    return int(match.group(1)) if match else None

# Define the load files
load_files = ["load_114.txt","load_171.txt", "load_1792.txt","load_370.txt","load_744.txt", "load_890.txt", "load_1103.txt", "load_1169.txt", "load_1192.txt", "load_2337.txt"]
base_path = "pecan/"
load_files = [base_path + file for file in load_files]
pv_files = [file.replace('load', 'PV') for file in load_files]

# Define other parameters
wfh_types = ['1', '2', '3']
operation_policies = ["optimal_unidirectional", "safe_unidirectional", "hybrid_unidirectional", "optimal_bidirectional", "hybrid_bidirectional", "safe_bidirectional"]

ev_data_files = {
    '1': 'ev_merged_T1.csv',
    '2': 'ev_merged_T23.csv',
    '3': 'ev_merged_T3.csv'
}

# Define the command template
command_template = "./bin/sim 1250 460 10 20 1 0.5 0.95 100 {load_file} {pv_file} 0.8 0.2 40.0 7.4 {op} ev_data/{file_name}"

# Initialize a DataFrame to store results
results_df = pd.DataFrame(columns=["Number", "Operation Policy", "WFH Type", "Battery", "PV", "Cost"])

# Iterate over all combinations of parameters and files
for load_file, pv_file in zip(load_files, pv_files):
    load_number = extract_load_number(load_file)
    for wfh_type in wfh_types:
        for op in operation_policies:
            # Construct and execute the command
            ev_file_name = ev_data_files[wfh_type]
            command = command_template.format(load_file=load_file, pv_file=pv_file, op=op, file_name=ev_file_name)
            print("Executing command: " + command)

            result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)

            # Process the output and extract relevant information
            output_parts = result.stdout.strip().split()
            battery, pv, cost = output_parts[0], output_parts[1], output_parts[2]
            print("Battery: " + battery + ", PV: " + pv + ", Cost: " + cost)

            # Append the results to the DataFrame
            results_df = results_df.append({
                "Number": load_number,
                "Operation Policy": op,
                "WFH Type": wfh_type,
                "Battery": float(battery),
                "PV": float(pv),
                "Cost": float(cost)
            }, ignore_index=True)

# Save the results to a CSV file
results_df.to_csv("evaluation_results_10_interm.csv", index=False)
