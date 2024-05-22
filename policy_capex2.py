import subprocess
import pandas as pd
import re
import os

def get_house_files():
    return [f"A_House_{i}.txt" for i in range(1, 60)] + [f"D_House_{i}.txt" for i in range(1, 42)]


# Base path for the files
base_path = os.path.abspath("./policy_data")

operations = ["safe_unidirectional", "hybrid_bidirectional"]
wfh_types = ["T1", "T2", "T3"]
solar_conditions = {"worst": "Lerwick_pv.txt", "best": "Weymouth_pv.txt"}

# Create or open the final output CSV file and prepare it for direct writing
with open("s_detached_capex_results.csv", "w") as output_file:
    output_file.write("House number,WFH Type,Operation,Solar,Battery,PV,Cost\n")
    
    low_values = []  # List to store house numbers with low PV or battery values

    for house_file in get_house_files():
        house_file_path = os.path.join(base_path, "Semi_Detached", house_file)
        
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
                    #print("Executing command: " + command)
                    
                    # Execute the command
                    result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
                    #print("Command output:", result.stdout)

                    if result.returncode != 0 or not result.stdout:
                        print("Command failed or produced no output.")
                        print("Executing command: " + command)
                    else:
                        # Extract and parse output
                        match = re.search(r"(\d+\.\d+) (\d+\.\d+) (\d+)", result.stdout)
                        if match:
                            b, c, cost = map(float, match.groups())
                            house_number = house_file.split('_')[2].split('.')[0]
                            output_file.write(f"{house_number},{wfh_type},{op},{solar_key},{b},{c},{cost}\n")
                            #print(f"Results for Semi-Detached {house_file} - Battery: {b}, PV: {c}, Cost: {cost}")
                            
                            if b < 0.5 or c < 0.5:
                                low_values.append(house_number)
                        else:
                            print("Failed to parse command output or incorrect output format.")
                            print("Executing command: " + command)

    print("Simulation complete. Houses with PV or Battery < 0.5:", ", ".join(low_values))
