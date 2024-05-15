# This generator does not allow for fine-grained control of the non-commuting trips, use ev_simulation_extended.py if you wish more fine grained control over the non-commuting trips.
# each trip is outputed separately and multiple trips on the same day are not grouped together, use merge_trips.py to merge overalpping trips.
import argparse
import numpy as np
import csv
import random

class ElectricVehicle:
    def __init__(self, battery_size, max_soc, min_soc, consumption):
        self.battery_size = battery_size
        self.max_soc = max_soc
        self.min_soc = min_soc
        self.consumption = consumption

    def compute_SOC_arr(self, dist_km):
        used_kwh = (dist_km * self.consumption) / 1000  
        soc_change = used_kwh / self.battery_size
        return max(self.max_soc * self.battery_size - soc_change, self.min_soc * self.battery_size)



def generate_trip_data(args, ev):
    trip_data = []
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wfh_days = {
        0: args.wfh_monday,
        1: args.wfh_tuesday,
        2: args.wfh_wednesday,
        3: args.wfh_thursday,
        4: args.wfh_friday
    }

    def reduce_soc(distance_km, current_soc):
        energy_used = (distance_km * ev.consumption) / 1000  # Convert Wh to kWh
        soc_after_trip = current_soc - energy_used
        return max(ev.min_soc * ev.battery_size, soc_after_trip)
# N_nc is the number of weekly non-commuting round trips
    average_non_commute_trips_per_day = (args.N_nc / 2) / 7
    average_speed_kmh = 50

    for day in range(args.days):
        week_day = day % 7
        is_wfh_day = wfh_days.get(week_day, 0) == 1
        is_weekend = week_day in [5, 6]
        # assume the EV is fully charged at the beginning of each day
        current_soc = ev.max_soc * ev.battery_size
        trips_today = []

        # Add commuting trips on non-WFH weekdays
        if not is_wfh_day and not is_weekend:
            commute_dist = random.uniform(args.C_dist - args.C_dist * 0.1, args.C_dist + args.C_dist * 0.1)
            t_dep, t_arr = sample_commute_times(args)
            soc_start = current_soc
            soc_end = reduce_soc(commute_dist, soc_start)
            commute_travel_time = (args.C_arr - args.C_dept) * 60  
            trips_today.append((weekdays[week_day], format_time(t_dep), f"{soc_start:.2f}", format_time(t_arr), f"{soc_end:.2f}", f"{commute_dist:.2f}", round(commute_travel_time)))
            current_soc = soc_end

        # Non-commuting trips
        num_non_commute_trips = np.random.poisson(average_non_commute_trips_per_day)
        for _ in range(num_non_commute_trips):
            t_dep, t_arr = sample_non_commute_times(args)
            # we assume that for non commuting trips, the EV is driving a 20% of the trip duration 
            travel_time_hours = (t_arr - t_dep) / 5
            # one-way non-commuting distance 
            non_commute_dist = travel_time_hours * average_speed_kmh /2
            soc_start = current_soc
            soc_end = reduce_soc(non_commute_dist, soc_start)
            non_commute_travel_time = travel_time_hours * 60  
            trips_today.append((weekdays[week_day], format_time(t_dep), f"{soc_start:.2f}", format_time(t_arr), f"{soc_end:.2f}", f"{non_commute_dist:.2f}", round(non_commute_travel_time)))
            current_soc = soc_end

        if not trips_today:
            trips_today.append((weekdays[week_day], "No trips", "32.0", "", "32.0"))

        trip_data.append((day + 1, trips_today))

    return trip_data


def format_time(time_float):
    """Converts time in float format to HH:MM format"""
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def sample_commute_times(args):
    """Sample departure and arrival times for commuting, ensuring consistency"""
    t_dep_hour = random.uniform(args.C_dept - 0.25, args.C_dept + 0.25)  # Departure time with small variance
    t_arr_hour = random.uniform(args.C_arr - 0.25, args.C_arr + 0.25)  # Arrival time with small variance
    
    while t_arr_hour <= t_dep_hour:
        t_arr_hour = random.uniform(args.C_arr - 0.25, args.C_arr + 0.25)

    return t_dep_hour, t_arr_hour

def sample_non_commute_times(args):
    """Randomly sample departure and arrival times for non-commuting trips, ensuring consistency"""
    t_dep_hour = random.uniform(8, 20)  # Assuming non-commuting trips can start between 8 AM and 8 PM
    trip_duration = random.uniform(0.5, 2)  # Duration between 30 minutes and 2 hours
    t_arr_hour = t_dep_hour + trip_duration

    if t_arr_hour >= 24:
        t_arr_hour -= 24

    return t_dep_hour, t_arr_hour

def write_to_csv(file_name, data):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Day", "Weekday", "Departure Time", "SOC on Departure", "Arrival Time", "SOC on Arrival", "Distance (km)", "Travel Time (min)"])
        for day, trips in data:
            for trip in trips:
                writer.writerow([day, *trip])


def run_simulation(args):
    # Run the simulation
    
    ev = ElectricVehicle(args.ev_battery, args.max_soc, args.min_soc, args.consumption)
    return generate_trip_data(args, ev)

''' ev_battery=battery_capacity,
            min_soc=min_soc / 100,  # Convert percentage to a decimal for the simulation
            max_soc=max_soc / 100,  # Convert percentage to a decimal for the simulation
            consumption=consumption,
            C_dist=C_dist,
            C_dept=C_dept_float,
            C_arr=C_arr_float,
            N_nc=N_nc,
            wfh_days=[wfh_monday, wfh_tuesday, wfh_wednesday, wfh_thursday, wfh_friday],  # Pass as a list
            num_days=365,  # Example number of days
            output_file='output/ev_trips.csv'  # Specify your output file path'''

# make sure that default values for all inputs are defined, make some inputs optional in FE, like C_dist

def setup_ev_simulation(ev_battery, max_soc, min_soc, consumption,C_dist,C_dept,C_arr,  N_nc, wfh_days, num_days, output_file):
    class Args:
        def __init__(self):
            self.ev_battery = ev_battery
            self.max_soc = max_soc
            self.min_soc = min_soc
            self.consumption = consumption
            self.days = num_days
            self.output = output_file
            # Set other parameters as needed or default values
            self.C_dist = C_dist  # Default commuting distance
            self.C_dept = C_dept # Default departure time
            self.C_arr = C_arr  # Default arrival time
            self.N_nc = N_nc    # Default number of non-commuting trips
            # WFH days setup (Example: all false)
            self.wfh_monday = wfh_days[0]
            self.wfh_tuesday = wfh_days[1]
            self.wfh_wednesday = wfh_days[2]
            self.wfh_thursday = wfh_days[3]
            self.wfh_friday = wfh_days[4]

    args = Args()
    trip_data = run_simulation(args)
    write_to_csv(args.output, trip_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample synthetic EV usage data.')
    # Argument setup
    parser.add_argument('--output', type=str, default='ev_usage.csv', help='Output file name')
    parser.add_argument('--days', type=int, default=365, help='Desired number of days sampled')
    parser.add_argument('--ev_battery', type=float, default=40, help='EV battery size in kWh')
    parser.add_argument('--max_soc', type=float, default=0.8, help='Maximum state of charge')
    parser.add_argument('--min_soc', type=float, default=0.2, help='Minimum state of charge')
    parser.add_argument('--consumption', type=float, default=164, help='Consumption in Wh/km')
    parser.add_argument('--wfh_monday', type=int, default=0, choices=[0, 1], help='WFH on Monday')
    parser.add_argument('--wfh_tuesday', type=int, default=0, choices=[0, 1], help='WFH on Tuesday')
    parser.add_argument('--wfh_wednesday', type=int, default=0, choices=[0, 1], help='WFH on Wednesday')
    parser.add_argument('--wfh_thursday', type=int, default=0, choices=[0, 1], help='WFH on Thursday')
    parser.add_argument('--wfh_friday', type=int, default=0, choices=[0, 1], help='WFH on Friday')
    parser.add_argument('--C_dist', type=float, default=20.0, help='Typical one-way commute distance in km')
    parser.add_argument('--C_dept', type=float, default=7.45, help='Departure time for commuting')
    parser.add_argument('--C_arr', type=float, default=17.30, help='Arrival time from commuting')
    parser.add_argument('--N_nc', type=int, default=5, help='Weekly number of non-commuting one-way trips')


    args = parser.parse_args()
    try:
        main(args)
    except ValueError as e:
        print(f"Input Error: {e}")
