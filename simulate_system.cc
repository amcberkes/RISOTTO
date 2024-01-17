#include <cmath>
#include <iostream>
#include <vector>
#include <utility>
#include "simulate_system.h"
#include "ev.h"
#include "common.h" 

using namespace std;

// parameters specified for an NMC cell with operating range of 1 C charging and discharging

void update_parameters(double n) {

	num_cells = n;

	a1_intercept = 0.0*num_cells;
	
	a2_intercept = kWh_in_one_cell*num_cells;
	
	alpha_d = a2_intercept*1.0;
	alpha_c = a2_intercept*1.0;
	return;
}

// decrease the applied (charging) power by increments of (1/30) until the power is 
// low enough to avoid violating the upper energy limit constraint.
double calc_max_charging(double power, double b_prev) {

	double step = power/30.0;

	for (double c = power; c >= 0; c -= step) {
		double upper_lim = a2_slope*(c/nominal_voltage_c) + a2_intercept;
		double b = b_prev + c*eta_c*T_u;
		if (b <= upper_lim) {
			return c;
		}
	}
	return 0;
}


// decrease the applied (discharging) power by increments of (1/30) until the power is
// low enough to avoid violating the lower energy limit constraint.
double calc_max_discharging(double power, double b_prev) {

	double step = power/30.0;

	for (double d = power; d >= 0; d -= step) {
		double lower_lim = a1_slope*(d/nominal_voltage_d) + a1_intercept;
		double b = b_prev - d*eta_d*T_u;
		if (b >= lower_lim) {
			return d;
		}
	}
	return 0;
}

double calc_max_charging_ev(double power, double ev_b)
{
	double step = power / 30.0;
	double upper_lim = max_soc * ev_battery_capacity;
	double ev_b_m = 0.0;

	for (double c = power; c >= 0; c -= step)
	{
		// Update battery SOC
		//std::cout << "EV_b before update: " << ev_b << "c: " << c << std::endl;
		ev_b_m = ev_b + c * eta_c_ev * T_u;
		//std::cout << "EV_b after update: " << ev_b << std::endl;

		// Check if the updated SOC is within the upper limit
		if (ev_b_m <= upper_lim)
		{
			return c;
		}
	}
	return 0;
}

double calc_max_discharging_ev(double power, double ev_b, double min_soc, double ev_battery_size)
{
	double step = power / 30.0;
	double lower_lim = min_soc * ev_battery_capacity;

	for (double d = power; d >= 0; d -= step)
	{
		// Update battery SOC
		ev_b = ev_b - d * eta_d_ev * T_u;

		// Check if the updated SOC is above the lower limit
		if (ev_b >= lower_lim)
		{
			return d;
		}
	}
	return 0;
}

int naive(const std::vector<EVStatus> &dailyStatuses, double ev_b, int currentHour)
{
	// Check if the EV is at home and can be charged
	if (dailyStatuses[currentHour].isAtHome)
	{
		return currentHour; // Start charging
	}
	return -1; // Do not charge if the EV is not at home
}

int lastp(const std::vector<EVStatus> &dailyStatuses, double ev_b, int currentHour)
{
	// Find the next departure hour
	int next_dept = -1;
	for (int hour = currentHour; hour < 24; ++hour)
	{
		if (!dailyStatuses[hour].isAtHome)
		{
			next_dept = hour;
			break;
		}
	}

	if (next_dept == -1)
	{
		return -1; // No trips remaining today
	}

	double diff = ev_battery_capacity - ev_b;
	int hours_needed = ceil(diff / alpha_c_ev);
	int latest_t = next_dept - hours_needed;
	return latest_t;
}

int mincost(const std::vector<EVStatus> &dailyStatuses, double ev_b, int currentHour, int t_ch)
{
	// Check if the EV is at home at the lowest cost hour
	if (dailyStatuses[t_ch].isAtHome)
	{
		return t_ch; // Start charging
	}
	return -1; // Do not charge if the EV is not at home at t_ch
}

std::pair<double, double> simulateEVCharging(std::vector<EVStatus> &dailyStatuses, int hour, int day, double last_soc)
{
		
		double ev_b = 0.0;
		// If the EV has just returned home, reset the SOC to the current hour's SOC
	//	std::cout << "Day: " << day << ", Hour: " << hour << ", Last SOC: " << last_soc << std::endl;

		if (!dailyStatuses[hour - 1].isAtHome && dailyStatuses[hour].isAtHome && hour != 0)
		{
				//std::cout << "HERE and read:  " << dailyStatuses[hour].currentSOC <<  std::endl;

			ev_b = dailyStatuses[hour].currentSOC;
		} else {
			ev_b = last_soc;
		}

		int chargeHour = -1;
		// Determine if we should charge this hour
		 if (selectedEVChargingPolicy == EVChargingPolicy::Last){
			chargeHour = lastp(dailyStatuses, ev_b, hour);
			std::cout << "In last" << std::endl;
		}
		else if (selectedEVChargingPolicy == EVChargingPolicy::Naive){
			 chargeHour = naive(dailyStatuses, ev_b, hour);
			 std::cout << "In naive" << std::endl;
		}  else if (selectedEVChargingPolicy == EVChargingPolicy::MinCost){
			 chargeHour = mincost(dailyStatuses, ev_b, hour, t_ch);
			 std::cout << "In mincost" <<  std::endl;
		} else {
			std::cout << "ERROR: Invalid EV charging policy selected" << std::endl;
		}
	//	std::cout << "EV Battery SOC before charging decision: " << ev_b << std::endl;

		double maxCharging = 0.0;
				if (chargeHour == hour)
			{
				// Simulate charging
				//TODO: here add how much power is available to charge the EV in one hour and call calc_max_charging_Ev with that input

				// Assuming charging rate of 7.4 kW. 
				double available_power = 7.4;
				maxCharging = calc_max_charging_ev(available_power, ev_b);
				ev_b += maxCharging * eta_c_ev * T_u; // Update SOC with charged amount

				if(maxCharging > 0)
				{
				//	std::cout << "Charging at hour " << hour << "day : " << day << ": Max Charging Power: " << maxCharging << std::endl;
				}
						//  << ", Updated SOC: " << ev_b << std::endl;
			}

		// Update current SOC in EVStatus and carry over to next hour
		dailyStatuses[hour].currentSOC = ev_b;
		last_soc = ev_b;
		//std::cout << "Final SOC for hour " << hour << ": " << ev_b << std::endl;

		return std::make_pair(maxCharging, last_soc);
}

// call it with a specific battery and PV size and want to compute the loss
double sim(vector<double> &load_trace, vector<double> &solar_trace, int start_index, int end_index, double cells, double pv, double b_0, std::vector<EVRecord> evRecords, std::vector<std::vector<EVStatus>> allDailyStatuses)
{

	update_parameters(cells);

	// set the battery
	double b = b_0*cells*kWh_in_one_cell; //0.5*a2_intercept
	int loss_events = 0;
	double load_deficit = 0;
	double load_sum = 0;

	int trace_length_solar = solar_trace.size();
	int trace_length_load = load_trace.size();

	double c = 0.0;
	double d = 0.0;
	double max_c = 0.0;
	double max_d = 0.0;
	int index_t_solar;
	int index_t_load;
	double last_soc = 32.0;
	int day = 0;
	int hour = 0;
	// loop through each hour 
	for (int t = start_index; t < end_index; t++) {

		// wrap around to the start of the trace if we hit the end.
		index_t_solar = t % trace_length_solar;
		index_t_load = t % trace_length_load;

		load_sum += load_trace[index_t_load];

		int index = t - start_index;
		hour = index % 24;
		day =  index / 24;
		int day2 = day +1;

		//EV CHARGING 
		std::pair<double, double> chargingResult = simulateEVCharging(allDailyStatuses[day], hour,day, last_soc);
		double maxCharging = chargingResult.first;
		last_soc = chargingResult.second;
		//std::cout << "Day: " << day2 << ", Hour: " << hour << ", Last SOC: " << last_soc << "EV Charging: " << maxCharging << std::endl;

		double hourly_laod = load_trace[index_t_load] + maxCharging;
		//double hourly_laod = load_trace[index_t_load] ;

		//---------------------------------------------------------------------------------------------------
		// first, calculate how much power is available for charging, and how much is needed to discharge
		c = fmax(solar_trace[index_t_solar]*pv - hourly_laod,0);
		d = fmax(hourly_laod- solar_trace[index_t_solar]*pv, 0);

		// constrain the power
		max_c = fmin(calc_max_charging(c,b), alpha_c);
		max_d = fmin(calc_max_discharging(d,b), alpha_d);


		// TODO: MODIFY HERE TO ADD OPERATING POLICIES

		b = b + max_c*eta_c*T_u - max_d*eta_d*T_u;

		// if we didnt get to discharge as much as we wanted, there is a loss
		if (max_d < d) {
			loss_events += 1;
			load_deficit += (d - max_d);
		}
	}

	if (metric == 0) {
		// lolp
		return loss_events/((end_index - start_index)*1.0);
	} else {
		// metric == 1, eue
		return load_deficit/(load_sum*1.0);
	}
}

// Run simulation for provides solar and load trace to find cheapest combination of
// load and solar that can meet the epsilon target
vector <SimulationResult> simulate(vector <double> &load_trace, vector <double> &solar_trace, int start_index, int end_index, double b_0, std::vector<EVRecord> evRecords, std::vector<std::vector<EVStatus>> allDailyStatuses) {

	// first, find the lowest value of cells that will get us epsilon loss when the PV is maximized
	// use binary search
	double cells_U = cells_max;
	double cells_L = cells_min;
	double mid_cells = 0.0;
	double loss = 0.0;

// binary search 
	while (cells_U - cells_L > cells_step) {

		mid_cells = (cells_L + cells_U) / 2.0;
		//simulate with PV max first 
		loss = sim(load_trace, solar_trace, start_index, end_index, mid_cells, pv_max, b_0, evRecords, allDailyStatuses);

		//cout << "sim result with " << a2_intercept << " kWh and " << pv_max << " pv: " << loss << endl;
		if (loss > epsilon) {
			cells_L = mid_cells;
		} else {
		 	// (loss <= epsilon)
			cells_U = mid_cells;
		}
	}

	// set the starting number of battery cells to be the upper limit that was converged on
	double starting_cells = cells_U;
	double starting_cost = B_inv*starting_cells + PV_inv * pv_max;
	double lowest_feasible_pv = pv_max;


	double lowest_cost = starting_cost;
	double lowest_B = starting_cells*kWh_in_one_cell;
	double lowest_C = pv_max;

	vector <SimulationResult> curve;
	// first point on the curve 
	curve.push_back(SimulationResult(starting_cells*kWh_in_one_cell, lowest_feasible_pv, starting_cost));
	//cout << "starting cells: " << starting_cells << endl;

	for (double cells = starting_cells; cells <= cells_max; cells += cells_step) {

		// for each value of cells, find the lowest pv that meets the epsilon loss constraint
		double loss = 0;
		while (true) {
			
			loss = sim(load_trace, solar_trace, start_index, end_index, cells, lowest_feasible_pv - pv_step, b_0, evRecords, allDailyStatuses);

			if (loss < epsilon) {
				//works
				lowest_feasible_pv -= pv_step;
			} else {
				break;
			}

			// this only happens if the trace is very short, since the battery starts half full
			// and can prevent loss without pv for a short time
			if (lowest_feasible_pv <= 0) {
				lowest_feasible_pv = 0;
				break;
			}
		}

		double cost = B_inv*cells + PV_inv*lowest_feasible_pv;

		curve.push_back(SimulationResult(cells*kWh_in_one_cell,lowest_feasible_pv, cost));

		if (cost < lowest_cost) {
			lowest_cost = cost;
			lowest_B = cells*kWh_in_one_cell;
			lowest_C = lowest_feasible_pv;
		}

	} 

	//return SimulationResult(lowest_B, lowest_C, lowest_cost);
	return curve;
}
