import streamlit as st
from pathlib import Path
import sys
import datetime


script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from utils.ev.ev_simulation_extended import setup_ev_simulation
from utils.ev.merge_trips import process_file


st.set_page_config(page_title='EV Details Input')
st.title("EV Details Input")
#st.write("Please enter your EV details and commute information below. The default values that are displayed are for a typical UK EV-user who commutes to work on every weekday with a Tesla Model S.")

st.info("Please enter your EV details and commute information below. The default values that are displayed are for a typical UK EV-user who commutes to work on every weekday with a Tesla Model S." " We recommend setting a lower and upper bound for the State-of-Charge when charging or discharching the EV battery to extend the battery lifetime.", icon="ℹ️")

with st.form("ev_commute_details"):
    # Existing EV Details as before
    battery_capacity = st.number_input("Battery Capacity of the EV (kWh)", min_value=1.0, value=60.0)
    connectivity = st.selectbox("Charging Connectivity of the EV", ["Unidirectional", "Bidirectional"])
    min_soc = st.slider("Min Desired State-of-Charge (% of total Battery Capacity of the EV)", 0, 100, 20)
    max_soc = st.slider("Max Desired State-of-Charge (% of total Battery Capacity of the EV)", 0, 100, 80)
    consumption = st.number_input("EV Consumption (Wh/km)", min_value=1.0, value=164.0)
    #st.write("Please enter your typical commuting trip details below.")
    # Correct the use of time_input
    C_dist = st.number_input("Typical Two-Way Commute Distance (km)", value=20.0)
    C_dept = st.time_input("Typical Commuting Trip Departure Time", value=datetime.time(7, 45))
    C_arr = st.time_input("Typical Commuting Trip Arrival Time at Home", value=datetime.time(17, 30))
    N_nc = st.number_input("Number of Non-Commuting One-Way Trips Per Week", min_value=0, value=5)

    # Work From Home Days with checkboxes
    st.write("Select your Work From Home days & days on which you do not commute to work with your EV:")
    wfh_monday = st.checkbox("Monday")
    wfh_tuesday = st.checkbox("Tuesday")
    wfh_wednesday = st.checkbox("Wednesday")
    wfh_thursday = st.checkbox("Thursday")
    wfh_friday = st.checkbox("Friday")

    # Submit button for the form
    submitted = st.form_submit_button("Submit EV and Commute Details")
    if submitted:
        # Convert times to hours as floats for simulation compatibility
        C_dept_float = C_dept.hour + C_dept.minute / 60.0
        C_arr_float = C_arr.hour + C_arr.minute / 60.0
        setup_ev_simulation(
            ev_battery=battery_capacity,
            min_soc=min_soc / 100,  # Convert percentage to a decimal for the simulation
            max_soc=max_soc / 100,  # Convert percentage to a decimal for the simulation
            consumption=consumption,
            C_dist=C_dist,
            C_dept=C_dept_float,
            C_arr=C_arr_float,
            N_nc=N_nc,
            wfh_days=[wfh_monday, wfh_tuesday, wfh_wednesday, wfh_thursday, wfh_friday],  
            num_days=365,  # Example number of days
            output_file='pages/utils/ev/ev_trips.csv'  
        )
        process_file('pages/utils/ev/ev_trips.csv', 'pages/data/ev.csv')
        st.success("Simulation completed successfully! Check the output file.")