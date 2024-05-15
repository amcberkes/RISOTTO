import requests
import json

def fetch_solar_data_from_api(lat, lon, output_file_path, us):
    url = ""
    base_url = "https://developer.nrel.gov/api/pvwatts/v8.json"
    api_key = "AQApgpuyM8tcFqhfwGyrXKJKQQofUlUt1bGfj9ke"

    if us == 0:
        url = f"{base_url}?api_key={api_key}&azimuth=180&system_capacity=4&losses=14&array_type=1&module_type=0&tilt=10&dataset=intl&timeframe=hourly&lat={lat}&lon={lon}"
    elif us == 1:
        url = f"{base_url}?api_key={api_key}&azimuth=180&system_capacity=4&losses=14&array_type=1&module_type=0&tilt=10&timeframe=hourly&lat={lat}&lon={lon}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Request failed: {response.status_code}")
        return

    data = response.json()

    # Write JSON data to intermediate file
    with open("json_interm.txt", "w") as json_file:
        json.dump(data, json_file, indent=4)
        print("JSON data written to: json_interm.txt")

    try:
        system_capacity = float(data["inputs"]["system_capacity"])
    except ValueError as ve:
        print(f"Invalid value for system_capacity: {ve}")
        return

    ac_values = data["outputs"]["ac"]

    # Write processed AC data to output file
    with open(output_file_path, "w") as out_file:
        for ac in ac_values:
            converted_value = (ac / system_capacity) / 1000  # Converting to kW
            out_file.write(f"{converted_value}\n")

    print(f"Processed AC data written to {output_file_path}")

# Example usage
#lat = "39.7392"
#lon = "-104.9903"
#output_file_path = "../../data/output.txt"
#us = 1  # 1 for US, 0 for international

#fetch_solar_data_from_api(lat, lon, output_file_path, us)
