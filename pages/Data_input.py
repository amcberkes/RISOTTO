import streamlit as st
from streamlit.components.v1 import html

import os
from pathlib import Path
import sys
import json
import numpy as np

script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from utils.uk_load.faraday import fetch_data
from utils.uk_load.faraday_postprocessing import process_files
#from utils.us_load.worker_us_load import run_trace_estimation
from utils.solar.solar import fetch_solar_data_from_api


st.set_page_config(page_title='Data Input')
st.title("Data Input")
st.markdown("Please provide the necessary data for the simulation:")

country = st.selectbox(
    "In which country are you located?",
   # ("US", "UK", "Germany"),
    ("US", "Germany", "UK"),
    index=1,  # Default to UK for demonstration
    help="Select the country where you are located to tailor the input fields accordingly."
)

#st.write("You selected:", country)

# Function to display inputs based on country
def display_inputs_for_country(country):
     # Latitude and Longitude inputs
    latitude = st.number_input("Enter Latitude", value=39.7392, key="latitude")
    longitude = st.number_input("Enter Longitude", value=-104.9903, key="longitude")

    if st.button("Submit"):
        if country == "US":
            fetch_solar_data_from_api(latitude, longitude, "pages/data/solar.txt", 1)
        elif country == "Germany" or country == "UK":
            fetch_solar_data_from_api(latitude, longitude, "pages/data/solar.txt", 0)

    st.write("Or upload a txt file with hourly solar generation over a year, normalized to 1kW of PV.")
    upload_file_solar = st.file_uploader("Upload Solar Data File", type=['txt'], key="upload_solar")

    st.subheader("Load Data")
    # Other inputs
    upload_file = st.file_uploader("Or upload a txt file with hourly load consumption over a year", type=['txt'], key="upload_load")

    # Display specific inputs based on the country
    
    if country == "UK":
        energy_rating = st.selectbox(
           "Energy Rating",
            ("A/B/C", "D/E/F/G"),
            help="Select the energy efficiency rating of your house."
        )
        number_habitable_rooms = st.selectbox(
            "Number of Habitable Rooms",
            ("3+", "2"),
            help="Select the number of habitable rooms in the property."
        )
        house_type = st.selectbox(
            "House Type",
            ("Terraced", "Semi-detached", "Detached", "Any House Types"),
            help="Select the type of house."
        )

        if st.button('Fetch Load Profile'):
            fetch_data(energy_rating, number_habitable_rooms, house_type)
            result_message = fetch_data(energy_rating, number_habitable_rooms, house_type)
            #st.text(result_message) 
            st.success("Load profile fetched successfully")
            # call post processing 
            input_directory = 'Single_load_files_uk'
            output_directory = 'pages/data/'
            process_files(input_directory, output_directory)
            st.success("Load file created")

        desired_self_consumption = st.slider("Desired level of self-consumption (%)", 0, 100, 50)
        optional_params = st.expander("Optional Parameters")
        with optional_params:
            desired_robustness = st.slider("Desired robustness of the results (%)", 80, 100, 90)
            max_pv_capacity = st.number_input("Maximum PV capacity on the roof (kW)", value=0.0)
            max_battery_capacity = st.number_input("Maximum battery capacity (kWh)", value=0.0)
            local_pv_price = st.number_input("Local price of PV per kW ($)", value=0.0)
            local_battery_price = st.number_input("Local price of stationary battery per kWh ($)", value=0.0)

   # else:  # US and Germany'''
    #if country == "US" or "Germany":  # This condition is always true, replace with the actual condition as needed

        # Create a numerical input field for each month of the year
      #  average_monthly_load = {}
       # st.write("Average Electricity Monthly Load (kWh)")
        #average_monthly_load["January"] = st.number_input("January", value=900.0)
       # average_monthly_load["February"] = st.number_input("February", value=800.0)
       # average_monthly_load["March"] = st.number_input("March", value=850.0)
       # average_monthly_load["April"] = st.number_input("April", value=750.0)
       # average_monthly_load["May"] = st.number_input("May", value=700.0)
       # average_monthly_load["June"] = st.number_input("June", value=850.0)
       # average_monthly_load["July"] = st.number_input("July", value=1000.0)
       # average_monthly_load["August"] = st.number_input("August", value=950.0)
      #  average_monthly_load["September"] = st.number_input("September", value=800.0)
      #  average_monthly_load["October"] = st.number_input("October", value=750.0)
      #  average_monthly_load["November"] = st.number_input("November", value=850.0)
      #  average_monthly_load["December"] = st.number_input("December", value=950.0)
            

        # Convert average_monthly_load to a 12-value np.array
      #  average_monthly_load_array = np.array(list(average_monthly_load.values()))
        # Submit button
      #  if st.button('Submit'):
       #     run_trace_estimation(average_monthly_load_array)
       #     st.success('Load estimation has been saved to load_us.txt')

      #  desired_self_consumption = st.slider("Desired level of self-consumption (%)", 0, 100, 50)
       # optional_params = st.expander("Optional Parameters")
       # with optional_params:
        #    desired_robustness = st.slider("Desired robustness of the results (%)", 80, 100, 90)
        #    max_pv_capacity = st.number_input("Maximum PV capacity on the roof (kW)", value=0.0)
        #    max_battery_capacity = st.number_input("Maximum battery capacity (kWh)", value=0.0)
        #    local_pv_price = st.number_input("Local price of PV per kW ($)", value=0.0)
        #    local_battery_price = st.number_input("Local price of stationary battery per kWh ($)", value=0.0)

       
# Render the appropriate input fields based on the selected country
display_inputs_for_country(country)
