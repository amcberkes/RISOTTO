import os
import asyncio
import json
import logging
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from asyncio.subprocess import create_subprocess_shell, PIPE
from utils.worker import run_simulation_sync 

# Constants
BINARY_FOLDER = os.getenv("ROBUST_SIZING_BINARY_PATH", "pages/bin/")
SIM = "sim"
SIMULATE_NUM_LOAD_TRACE = 4
SIZING_LOSS_TARGETS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9]

# Logging setup
logging.basicConfig(level=logging.DEBUG, filename='simulation.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

async def run_robust_sizing(method, estimation_type, pv_price_per_kw, battery_price_per_kwh,
                            pv_max_kw, battery_max_kwh, epsilon_target, confidence_level, days_in_sample,
                            load_file, solar_file, max_soc, min_soc, ev_battery_capacity, charging_rate, operation_policy, path_to_ev_data):

    logging.debug(f"Starting run_robust_sizing, method={method}, estimation_type={estimation_type}, epsilon_target={epsilon_target}")

    args = [BINARY_FOLDER + SIM, pv_price_per_kw, battery_price_per_kwh, pv_max_kw, battery_max_kwh, 1,
            epsilon_target, confidence_level, days_in_sample, load_file, solar_file, max_soc, min_soc,
            ev_battery_capacity, charging_rate, operation_policy, path_to_ev_data]

    arg = " ".join(map(str, args))

    # Log the exact subprocess call for debugging
    print(f"Subprocess call: {arg}")
    logging.debug(f"Subprocess call: {arg}")

    p = await create_subprocess_shell(arg, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p_stdout, p_stderr = await p.communicate()

    logging.debug(f"finishing run_robust_sizing, method={method}, estimation_type={estimation_type}, epsilon_target={epsilon_target}")

    return p_stdout.decode(), p_stderr.decode(), epsilon_target, arg

def parse_sizing_result(result):
    out, err, target, args = result
    if err:
        return {
            "success": 0,
            "target": target,
            "args": args,
            "stdout": out,
            "error": err
        }

    try:
        returns = list(map(float, out.split()))
    except ValueError as e:
        logging.error(f"Error parsing output: {e}")
        return {
            "success": 0,
            "target": target,
            "args": args,
            "stdout": out,
            "error": f"Error parsing output: {e}"
        }

    if returns[2] == float('inf'):
        return {
            "success": 1,
            "feasible": 0,
            "target": target
        }
    else:
        return {
            "success": 1,
            "feasible": 1,
            "target": target,
            "battery_kwh": returns[0],
            "pv_kw": returns[1],
            "total_cost": returns[2]
        }

async def run_simulations(method, estimation_type, pv_price_per_kw, battery_price_per_kwh,
                          pv_max_kw, battery_max_kwh, confidence_level, days_in_sample,
                          load_file, solar_file, max_soc, min_soc, ev_battery_capacity, charging_rate,
                          operation_policy, path_to_ev_data, desired_epsilon):

    tasks = []
    targets = [desired_epsilon]

    for target in targets:
        tasks.append(run_robust_sizing(
            method, estimation_type, pv_price_per_kw, battery_price_per_kwh, pv_max_kw, battery_max_kwh,
            target, confidence_level, days_in_sample, load_file, solar_file, max_soc, min_soc,
            ev_battery_capacity, charging_rate, operation_policy, path_to_ev_data
        ))

    results = await asyncio.gather(*tasks)
    parsed_results = list(map(parse_sizing_result, results))

    return parsed_results

# Wrapper function to run the async function
def run_simulation_sync(*args, **kwargs):
    return asyncio.run(run_simulations(*args, **kwargs))

# Streamlit part
# Set up the page configuration
st.set_page_config(page_title='Results')

# Title of the Streamlit app
st.title("Results")

# Function to delete files
def delete_files(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

# Example input data, replace with actual input collection as needed
input_data = {
    "method": "sim",
    "estimation_type": 1,
    "pv_price_per_kw": 1000,
    "battery_price_per_kwh": 500,
    "pv_max_kw": 15,
    "battery_max_kwh": 60,
    "confidence_level": 0.85,
    "days_in_sample": 100,
    "load_file": "pages/data/load.txt",
    "solar_file": "pages/data/solar.txt",
    "max_soc": 0.8,
    "min_soc": 0.2,
    "ev_battery_capacity": 60.0,
    "charging_rate": 7.4,
    "operation_policy": "safe_unidirectional",
    "path_to_ev_data": "pages/data/ev.csv",
    "desired_epsilon": 0.7
}

# Button to run the simulation
if st.button('Run Simulation'):
    results = run_simulation_sync(**input_data)

    # Prepare the DataFrame
    chart_data_list = []
    for res in results:
        if res.get("success") == 1:
            chart_data_list.append({
                "cost": res.get("total_cost", np.nan),
                "pv": res.get("pv_kw", np.nan),
                "battery": res.get("battery_kwh", np.nan),
                "self-consumption": res.get("target", np.nan)
            })
    
    if not chart_data_list:
        st.error("No successful simulation results to display.")
    else:
        chart_data = pd.DataFrame(chart_data_list)

        # Check if the 'cost' column exists and has valid data
        if 'cost' not in chart_data or chart_data['cost'].isnull().all():
            st.error("Cost data is not available in the simulation results.")
        else:
            # Find recommended values based on minimum cost
            recommended = chart_data.loc[chart_data['cost'].idxmin()]
            st.write("\n")
            st.write("\n")
            # Display recommended configuration
            st.subheader('Recommended System Configuration')
            col1, col2, col3 = st.columns(3)
            col1.metric("Recommended PV Size", f"{recommended['pv']} kW")
            col2.metric("Recommended Battery Size", f"{recommended['battery']} kWh")
            col3.metric("Estimated Cost", f"${recommended['cost']:,.0f}")

            # Add spacing between sections
            st.write("\n")  # Add a blank line for more space
            st.write("\n")

            # Using Plotly Express to create an interactive line chart
            fig = px.line(
                chart_data, 
                x="self-consumption", 
                y="cost",
                title="Cost vs Self-Consumption",
                markers=True,  # Adds markers to line points
            )

            # Add hover data
            fig.update_traces(
                mode='markers+lines', 
                hovertemplate='Self-Consumption: %{x}<br>Cost: %{y}<br>PV: %{customdata[0]} kW<br>Battery: %{customdata[1]} kWh',
                customdata=np.stack((chart_data['pv'], chart_data['battery']), axis=-1)
            )

            # Add x-axis and y-axis labels
            fig.update_layout(
                xaxis_title="Self Consumption",
                yaxis_title="Cost ($)",
                hovermode="x unified"
            )

            # Show plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # Convert DataFrame to CSV for download
            csv = chart_data.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='results_data.csv',
                mime='text/csv',
            )

            # Delete load and solar files
            delete_files(input_data["load_file"], input_data["solar_file"])
