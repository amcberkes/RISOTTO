import os
from datetime import datetime
import numpy as np
import logging
from utils.us_load.simulate_models import KnnARIMAModelSimulator

SIMULATE_NUM_LOAD_TRACE = 4

def run_simulate_load_trace(load_monthly_params):
    simulator = KnnARIMAModelSimulator(compress_pickle=False)
    gen_hourly, knn_stations = simulator.simulate_hourly_data(load_monthly_params, SIMULATE_NUM_LOAD_TRACE, True)
    return gen_hourly, knn_stations

def run_trace_estimation(load_params):
    load_list, knn_stations = run_simulate_load_trace(load_params)
    load_arr = np.hstack(load_list)
    os.makedirs('../../data/', exist_ok=True)
    save_path = '../../data/load_us.txt'
    np.savetxt(save_path, load_arr, fmt='%0.8f')
    return load_arr

# Example usage
#average_monthly_load_array = [0.0] * 12  # Replace with actual values
#run_trace_estimation(average_monthly_load_array)
