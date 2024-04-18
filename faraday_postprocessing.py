import os
import json
from datetime import datetime, timedelta

def convert_half_hourly_to_hourly(half_hourly_data):
    return [sum(map(float, half_hourly_data[i:i+2])) for i in range(0, len(half_hourly_data), 2)]

def process_files(input_dir, output_dir, rating, count):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_date = datetime(2023, 1, 1)  # Non-leap year start
    os.makedirs(output_dir, exist_ok=True)

    for house_number in range(1, count + 1):
        house_data = []
        current_date = start_date
        while current_date.year == 2023:
            weekday = current_date.strftime("%A")
            month = current_date.strftime("%B")
            filename = f"{rating}_{month}_{weekday}.json"
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, 'r') as file:
                data = json.load(file)
                kwh_data = data['message']['results'][0]['kwh']
                # Process all 48 half-hour data points to sum to 24 hours
                half_hourly_loads = kwh_data[house_number-1]
                hourly_loads = convert_half_hourly_to_hourly(half_hourly_loads)
                house_data.extend(hourly_loads)


            current_date += timedelta(days=1)

        output_filepath = os.path.join(output_dir, f"{rating}_House_{house_number}.txt")
        with open(output_filepath, 'w') as f:
            for load in house_data:
                f.write(f"{load}\n")

        print(f"Data for House {house_number} saved to {output_filepath}")

input_directory = 'Semi_Detached'
output_directory = 'Semi_Detached_100'
process_files(input_directory, output_directory, 'A', 59)  # For A-rated houses
process_files(input_directory, output_directory, 'D', 41)  # For D-rated houses
