import os
import requests
import json

API_URL = "https://faraday-api-gateway-28g4j071.nw.gateway.dev/v3/predict/"
API_KEY = "your_api_key_here"
HEADERS = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'x-api-key': 'AIzaSyAIrHGf-HHhCxwj8Po7oDl2GlEzyAB4oOg'
}
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS_OF_YEAR = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
ENERGY_RATINGS = [
    ("A", 59, "A/B/C"),  # Include both label and JSON value
    ("D", 41, "D/E/F/G")
]

# Ensure output directory exists
os.makedirs('Terraced_HP', exist_ok=True)

# Function to send API request
def send_request(day, month, energy_rating_label, energy_rating_json, count):
    data = {
        "day_of_week": day,
        "month_of_year": month,
        "population": [
            {
                "name": "Terraced_energy_rating_day_month",
                "count": count,
                "attributes": {
                    "energy_rating": energy_rating_json,
                    "number_habitable_rooms": "3+",
                    "urbanity": "Urban",
                    "property_type_1": "House",
                    "property_type_2": "Terraced",
                    "is_mains_gas": "Has Mains Gas",
                    "lct": ["Has Solar Photovoltaics", "Has Heat Pump"]
                }
            }
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, json=data)
    return response.json()

# Main execution loop
for month in MONTHS_OF_YEAR:
    for day in DAYS_OF_WEEK:
        for label, count, json_value in ENERGY_RATINGS:
            result = send_request(day, month, label, json_value, count)
            file_name = f"Terraced_HP/{label}_{month}_{day}.json"  # Simpler file naming
            with open(file_name, 'w') as f:
                json.dump(result, f, indent=4)
            print(f"Saved data to {file_name}")

print("All data fetched and saved.")
