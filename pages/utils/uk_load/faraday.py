import os
import requests
import json
import logging
import time

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_URL = "https://faraday-api-gateway-28g4j071.nw.gateway.dev/v3/predict/"
API_KEY = "AIzaSyAIrHGf-HHhCxwj8Po7oDl2GlEzyAB4oOg"
HEADERS = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'x-api-key': API_KEY
}
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS_OF_YEAR = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Ensure output directory exists
os.makedirs('Single_load_files_uk', exist_ok=True)

def send_request(day, month, energy_rating, number_of_habitable_rooms, house_type):
    data = {
        "day_of_week": day,
        "month_of_year": month,
        "population": [{
            "name": "User_load",
            "count": 1,
            "attributes": {
                "energy_rating": energy_rating,
                "number_of_habitable_rooms": number_of_habitable_rooms,
                "urbanity": "Urban",
                "property_type_1": "House",
                "property_type_2": house_type,
                "is_mains_gas": "Has Mains Gas",
                "lct": ["Has No LCTs"]
            }
        }]
    }
    logging.debug(f"Sending data to API: URL: {API_URL}, Headers: {HEADERS}, Data: {data}")

    try:
        response = requests.post(API_URL, headers=HEADERS, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error("Request timed out, waiting for 1 minute before retrying...")
        time.sleep(60)
        return send_request(day, month, energy_rating, number_of_habitable_rooms, house_type)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return f"HTTP error occurred: {http_err} - Response: {response.text}"
    except Exception as err:
        logging.error(f"An unexpected error occurred: {str(err)}")
        return f"An unexpected error occurred: {str(err)}"

def fetch_data(energy_rating, number_of_habitable_rooms, house_type):
    status_messages = []
    for month in MONTHS_OF_YEAR:
        for day in DAYS_OF_WEEK:
            result = send_request(day, month, energy_rating, number_of_habitable_rooms, house_type)
            logging.debug(f"API response for {day} of {month}: {result}")
            if isinstance(result, dict):  # Assuming successful response returns a dictionary
                file_name = f"Single_load_files_uk/{month}_{day}.json"
                try:
                    with open(file_name, 'w') as f:
                        json.dump(result, f, indent=4)
                    status_messages.append(f"Saved data to {file_name}")
                except IOError as e:
                    logging.error(f"Failed to write data for {month} {day}: {str(e)}")
                    status_messages.append(f"Failed to write data for {month} {day}: {str(e)}")
            else:
                status_messages.append(result)  # result contains the error message
    if not status_messages:
        return "No data processed."
    else:
        return "\n".join(status_messages)

# Example usage
#result = fetch_data("A/B/C", "3+", "Terraced")
#print(result)
