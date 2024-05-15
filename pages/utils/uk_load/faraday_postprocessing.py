import os
import json
from datetime import datetime, timedelta

def convert_half_hourly_to_hourly(half_hourly_data):
    """Convert lists of half-hourly energy readings into hourly totals."""
    return [sum(map(float, half_hourly_data[i:i+2])) for i in range(0, len(half_hourly_data), 2)]

def process_files(input_dir, output_dir):
    """Process all files in the given directory and aggregate into yearly data."""
    start_date = datetime(2023, 1, 1)
    os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
    yearly_data = []

    current_date = start_date
    while current_date.year == 2023:
        weekday = current_date.strftime("%A")
        month = current_date.strftime("%B")
        filename = f"{month}_{weekday}.json"
        filepath = os.path.join(input_dir, filename)

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    half_hourly_loads = data['message']['results'][0]['kwh'][0]
                    hourly_loads = convert_half_hourly_to_hourly(half_hourly_loads)
                    yearly_data.extend(hourly_loads)
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
        else:
            print(f"File not found: {filepath}")

        current_date += timedelta(days=1)

    output_filepath = os.path.join(output_dir, "loads.txt")
    if yearly_data:
        with open(output_filepath, 'w') as f:
            for load in yearly_data:
                f.write(f"{load}\n")
        print(f"All data combined and saved to {output_filepath}")
    else:
        print("No data collected to write to the file.")

if __name__ == '__main__':
    input_directory = 'Single_load_files_uk'
    output_directory = '../../data/'  # Update to the correct relative path
    process_files(input_directory, output_directory)
