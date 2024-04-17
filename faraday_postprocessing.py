import os
import json

def convert_half_hourly_to_hourly(half_hourly_data):
    """Converts half-hourly load data to hourly by summing consecutive pairs of float values."""
    return [sum(map(float, half_hourly_data[i:i+2])) for i in range(0, len(half_hourly_data), 2)]

def process_files(directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)  # Ensure output directory exists

    files = sorted(f for f in os.listdir(directory) if f.endswith('.json'))
    
    for file in files:
        filepath = os.path.join(directory, file)
        with open(filepath, 'r') as f:
            data = json.load(f)
            kwh_data = data['message']['results'][0]['kwh']
            
            if file.startswith('A_'):
                num_houses = 59
                energy_rating = 'A'
            elif file.startswith('D_'):
                num_houses = 41
                energy_rating = 'D'
            else:
                continue
            
            for house_number in range(1, num_houses + 1):
                try:
                    half_hourly_loads = kwh_data[house_number - 1]
                    hourly_loads = convert_half_hourly_to_hourly(half_hourly_loads)
                    
                    output_file_path = os.path.join(output_directory, f"Terraced_{energy_rating}_House_{house_number}.txt")
                    
                    with open(output_file_path, 'a') as file:
                        file.write('\n'.join(map(str, hourly_loads)) + '\n')
                        
                except IndexError:
                    print(f"IndexError in file {file}: House number {house_number} out of range.")

directory = 'Terraced'
output_directory = 'Terraced_100'

process_files(directory, output_directory)
