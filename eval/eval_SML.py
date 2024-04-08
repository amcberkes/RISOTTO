import subprocess
import pandas as pd

# Define the load and PV file names
load_files = ["load_114.txt","load_171.txt", "load_252.txt","load_370.txt","load_545.txt","load_744.txt", "load_890.txt", "load_1103.txt", "load_1169.txt", "load_1192.txt"]


# Base path for the files
base_path = "pecan/"



# Update load_files and pv_files to include the full path
load_files = [base_path + file for file in load_files]
pv_files = [file.replace('load', 'PV') for file in load_files]

# Define other parameters
wfh_types = ['1', '2', '3']
commute_distances = ['S', 'M', 'L']
ev_data_files = {
    ('1', 'S'): 'ev_data_T1_S.csv',
    ('1', 'M'): 'ev_data_T1_M.csv',
    ('1', 'L'): 'ev_data_T1_L.csv',
    ('2', 'S'): 'ev_data_T2_S.csv',
    ('2', 'M'): 'ev_data_T2_M.csv',
    ('2', 'L'): 'ev_data_T2_L.csv',
    ('3', 'S'): 'ev_data_T3_S.csv',
    ('3', 'M'): 'ev_data_T3_M.csv',
    ('3', 'L'): 'ev_data_T3_L.csv'
}

# Define the command template
command_template = "./bin/sim 1250 460 70 250 1 0.3 0.85 100 {load_file} {pv_file} 0.8 0.2 40.0 7.4 hybrid_unidirectional ev_data_SML/nc/{file_name}"

# Initialize a DataFrame to store results
results_df = pd.DataFrame(columns=["WFH Type", "Commute Distance", "Battery", "PV", "Cost"])

# Iterate over all combinations of parameters and files
for load_file, pv_file in zip(load_files, pv_files):
    for wfh_type in wfh_types:
        for c_dist in commute_distances:
            # Construct and execute the command
            ev_file_name = ev_data_files[(wfh_type, c_dist)]
            command = command_template.format(load_file=load_file, pv_file=pv_file, file_name=ev_file_name)
            print("Executing command: " + command)

            result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)

            # Process the output and extract relevant information
            output_parts = result.stdout.strip().split()
            battery = output_parts[0]  # Assuming 'Battery: value' format
            pv = output_parts[1]  # Assuming 'PV: value' format
            cost = output_parts[2]  # Assuming 'Cost: value' format
            print("Battery: " + battery + ", PV: " + pv + ", Cost: " + cost)

            # Append the results to the DataFrame
            results_df = results_df.append({
                "WFH Type": wfh_type,
                "Commute Distance": c_dist,
                "Battery": float(battery),
                "PV": float(pv),
                "Cost": float(cost)
            }, ignore_index=True)

# Save the results to a CSV file
results_df.to_csv("hybrid_unidirectional_evaluation_results.csv", index=False)
