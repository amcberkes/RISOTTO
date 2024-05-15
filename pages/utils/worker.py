# worker.py
import os
import asyncio
import json
import logging
from asyncio.subprocess import create_subprocess_shell, PIPE

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

    logging.debug(f"Subprocess stdout: {p_stdout.decode()}")
    logging.debug(f"Subprocess stderr: {p_stderr.decode()}")

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
    targets = [desired_epsilon] + SIZING_LOSS_TARGETS

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

if __name__ == "__main__":
    # Example usage: replace with actual input values or read from a configuration file
    input_data = {
        "method": "sim",
        "estimation_type": "lolp",
        "pv_price_per_kw": 1000,
        "battery_price_per_kwh": 500,
        "pv_max_kw": 10,
        "battery_max_kwh": 40,
        "confidence_level": 0.95,
        "days_in_sample": 30,
        "load_file": "pages/data/load.txt",
        "solar_file": "pages/data/solar.txt",
        "max_soc": 0.9,
        "min_soc": 0.2,
        "ev_battery_capacity": 40.0,
        "charging_rate": 7.4,
        "operation_policy": "optimal_unidirectional",
        "path_to_ev_data": "path/to/ev/data.txt",
        "desired_epsilon": 0.15
    }
    results = run_simulation_sync(**input_data)
    print(json.dumps(results, indent=4))
