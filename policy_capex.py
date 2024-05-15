import subprocess
import pandas as pd
import re
import os

# Function to get paths of house files for each archetype
def get_house_files(archetype):
    return [f"A_House_{i}.txt" for i in range(1, 60)] + [f"D_House_{i}.txt" for i in range(1, 42)]

# Base path for the files
base_path = os.path.abspath("./policy_data")

# Archetypes and their corresponding folders
archetypes = ["Detached", "Semi_Detached", "Terraced"]
operations = ["safe_unidirectional", "hybrid_bidirectional"]
wfh_types = ["T1", "T2", "T3"]
solar_conditions = {"worst": "Lerwick_pv.txt", "best": "Weymouth_pv.txt"}

# Prepare to collect overall results
all_results = []

# Iterate over each archetype
for archetype in archetypes:
    results = []  # List to store results for the current archetype

    for house_file in get_house_files(archetype):
        house_file_path = os.path.join(base_path, archetype, house_file)
        
        if not os.path.exists(house_file_path):
            print(f"Error: File does not exist - {house_file_path}")
            continue
        
        for wfh_type in wfh_types:
            for op in operations:
                for solar_key, solar_file_name in solar_conditions.items():
                    solar_file_path = os.path.join(base_path, "Solar_UK", solar_file_name)
                    
                    if not os.path.exists(solar_file_path):
                        print(f"Error: Solar file does not exist - {solar_file_path}")
                        continue
                    
                    # Construct command
                    command = f"./bin/sim 2100 480 15 25 1 0.7 0.85 100 {house_file_path} {solar_file_path} 0.8 0.2 60.0 7.4 {op} {base_path}/ev_UK/merged_{wfh_type}_UK.csv"
                    print("Executing command: " + command)
                    
                    # Execute the command
                    result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
                    print("Command output:", result.stdout)

                    # Extract and parse output
                    match = re.search(r"(\d+\.\d+) (\d+\.\d+) (\d+\.\d+)", result.stdout)
                    if match:
                        b, c, cost = map(float, match.groups())
                        results.append({
                            "Archetype": archetype,
                            "House number": house_file.split('_')[2].split('.')[0],
                            "WFH Type": wfh_type,
                            "Operation": op,
                            "Solar": solar_key,
                            "Battery": b,
                            "PV": c,
                            "Cost": cost
                        })
                        print(f"Results for {archetype} {house_file} - Battery: {b}, PV: {c}, Cost: {cost}")

    # Save results for the current archetype to a CSV file
    df_archetype = pd.DataFrame(results)
    df_archetype.to_csv(f"{archetype}_capex_results.csv", index=False)
    print(f"Saved {archetype} results to CSV.")

    # Append results of the current archetype to the overall results list
    all_results.extend(results)

# Convert overall results to DataFrame and save to CSV
df_all_results = pd.DataFrame(all_results)
df_all_results.to_csv("capex_results.csv", index=False)
print("Saved aggregated results to CSV.")
