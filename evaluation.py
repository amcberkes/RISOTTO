import subprocess
import csv

# Define the parameter ranges
wfh_types = ['1', '2', '3']
ev_charging_policies = ["naive", "last", "min_cost"]
operation_policies = ["unidirectional", "most_sustainable", "min_storage", "maximise_solar_charging"]
ev_data_files = {
    '1': 'ev_T1.csv',
    '2': 'ev_T23.csv',
    '3': 'ev_T3.csv'
}

# Define the command template
command_template = "./bin/sim 2000 500 10 225 1 0.1 0.95 100 new_dheli_load.txt new_dheli_pv.txt 0.8 0.2 40.0 4 7.4 {ev} {op} ev_data/{file_name}"

# Define the output CSV file
output_csv = "evaluation_results.csv"

# Create and open the output CSV file
with open(output_csv, 'w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["WFH Type", "EV Charging Policy", "Operation Policy", "Battery", "PV", "Cost"])

    # Iterate over all combinations of parameters
    for wfh_type in wfh_types:
        for ev in ev_charging_policies:
            for op in operation_policies:
                # Get the EV data file name for the current WFH type
                ev_file_name = ev_data_files[wfh_type]

                # Construct the command
                command = command_template.format(ev=ev, op=op, file_name=ev_file_name)

                print("Executing command: " + command)
                # Execute the command
                result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)

                # Process the output and extract relevant information
                output_parts = result.stdout.strip().split()
                battery = output_parts[0]  # Assuming 'Battery: value' format
                pv = output_parts[1]  # Assuming 'PV: value' format
                cost = output_parts[2]  # Assuming 'Cost: value' format
                print("Battery: " + battery + ", PV: " + pv + ", Cost: " + cost)

                # Write the row to the CSV file
                writer.writerow([wfh_type, ev, op, battery, pv, cost])
