
import subprocess
import pandas as pd

# Define the load and PV file names
# mayvve delete 5439
#load_files3 = ["load_114.txt","load_171.txt", "load_252.txt","load_370.txt","load_545.txt","load_744.txt", "load_890.txt", "load_1103.txt", "load_1169.txt", "load_1192.txt", "load_1792.txt", "load_2018.txt", "load_2072.txt", "load_2199.txt", "load_2337.txt", "load_2638.txt","load_2814.txt","load_2980.txt", "load_2986.txt", "load_3134.txt","load_3367.txt", "load_3482.txt", "load_3527.txt","load_4357.txt","load_4526.txt","load_5129.txt","load_5439.txt","load_5545.txt","load_5615.txt","load_5738.txt","load_5796.txt","load_5874.txt","load_5892.txt","load_6121.txt","load_6266.txt", "load_6423.txt","load_6578.txt", "load_7429.txt", "load_7741.txt","load_7788.txt","load_7850.txt","load_7940.txt","load_7989.txt","load_7989.txt","load_8084.txt","load_8197.txt","load_8236.txt","load_8317.txt", "load_8419.txt", "load_8626.txt","load_9121.txt","load_9647.txt",]
load_files = ["load_114.txt","load_171.txt", "load_1792.txt","load_370.txt","load_744.txt", "load_890.txt", "load_1103.txt", "load_1169.txt", "load_1192.txt"]
#load_files = ["load_8626.txt"]


# Base path for the files
base_path = "pecan/"

# Update load_files and pv_files to include the full path
load_files = [base_path +  file for file in load_files]
pv_files = [file.replace('load', 'PV') for file in load_files]

# Define other parameters
wfh_types = ['1', '2', '3']
operation_policies = ["optimal_bidirectional", "hybrid_bidirectional","optimal_unidirectional", "safe_unidirectional", "hybrid_unidirectional",  "safe_bidirectional"]

#operation_policies = [ "optimal_bidirectional","hybrid_bidirectional"]

ev_data_files = {
    '1': 'ev_merged_T1.csv',
   '2': 'ev_merged_T23.csv',
    '3': 'ev_merged_T3.csv'
}
# 2690 460 50 200 1 0.5 0.95 100
# Define the command template
command_template = "./bin/sim 1250 460 50 100 1 0.4 0.95 100 {load_file} {pv_file} 0.8 0.2 40.0 7.4  {op} ev_data/{file_name}"

# Initialize a DataFrame to store results
results_df = pd.DataFrame(columns=["WFH Type", "Operation Policy", "Battery", "PV", "Cost"])

# Iterate over all combinations of parameters and files
for load_file, pv_file in zip(load_files, pv_files):
    for wfh_type in wfh_types:
            for op in operation_policies:
                # Construct and execute the command
                ev_file_name = ev_data_files[wfh_type]
                command = command_template.format(load_file=load_file, pv_file=pv_file,  op=op, file_name=ev_file_name)
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
                    "Operation Policy": op,
                    "Battery": float(battery),
                    "PV": float(pv),
                    "Cost": float(cost)
                }, ignore_index=True)

# Group by WFH Type and Operation Policy, and calculate the average values
avg_results_df = results_df.groupby(["WFH Type", "Operation Policy"]).mean().reset_index()

# Save the averaged results to a CSV file
avg_results_df.to_csv("averaged_evaluation_results_9_0.4.csv", index=False)
