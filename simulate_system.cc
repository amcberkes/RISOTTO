#include <cmath>
#include <iostream>
#include <vector>
#include <utility>
#include "simulate_system.h"
#include "ev.h"
#include "common.h" 

using namespace std;

int loss_events = 0;
double load_deficit = 0;
double load_sum = 0;
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

std::pair<double, double> unidirectional(double b, double ev_b, double c, double d, bool z, double max_c, double max_d)
{
	double max_c_ev = 0.0;
	if (c > 0)
	{
		b = b + max_c * eta_c * T_u;
		double res = c - max_c;
		if (res > 0)
		{
			max_c_ev = fmin(calc_max_charging_ev(res, ev_b), alpha_c_ev);
			ev_b = ev_b + max_c_ev * eta_c_ev * T_u;
		}
	}
	if (d > 0)
	{
		b = b - max_d * eta_d * T_u;
		if (max_d < d)
		{
			loss_events += 1;
			load_deficit += (d - max_d);
		}
	}

	return std::make_pair(ev_b, b);
}

std::pair<double, double> minstorage(double b, double ev_b, double c, double d, bool z, double max_c, double max_d)
{
	double max_c_ev = fmin(calc_max_charging_ev(c, ev_b), alpha_c_ev);
	double max_d_ev = fmin(calc_max_discharging_ev(d, ev_b, min_soc, ev_battery_capacity), alpha_d_ev);

	if (c > 0)
	{
		ev_b = ev_b + max_c_ev * eta_c_ev * T_u;
		double res = c - max_c_ev;
		if (res > 0)
		{
			max_c = fmin(calc_max_charging(res, b), alpha_c);
			b = b + max_c * eta_c * T_u;
		}
	}
	if (d > 0)
	{
		if (z == true)
		{
			// cannot discharge ev
			b = b - max_d * eta_d * T_u;
			if (max_d < d)
			{
				loss_events += 1;
				load_deficit += (d - max_d);
			}
		}
		else
		{
			ev_b = ev_b - max_d_ev * eta_d_ev * T_u;
			double res = d - max_d_ev;
			if (res > 0)
			{
				max_d = fmin(calc_max_discharging(res, b), alpha_d);
				b = b - max_d * eta_d * T_u;
				res = res - max_d;

				if (res > 0)
				{
					loss_events += 1;
					load_deficit += res;
				}
			}
		}
	}

	return std::make_pair(ev_b, b);
}

std::pair<double, double> rDegradation(double b, double ev_b, double c, double d, bool z, double max_c, double max_d)
{
	// charge: 1=stationary, 2= ev, 3 = verloren
	//  discharge: 1= stationary, 2 = ev, 3= grid
	double max_c_ev;
	double max_d_ev;
	if (c > 0)
	{
		b = b + max_c * eta_c * T_u;
		double res = c - max_c;
		if (res > 0)
		{
			max_c_ev = fmin(calc_max_charging_ev(res, ev_b), alpha_c_ev);
			ev_b = ev_b + max_c_ev * eta_c_ev * T_u;
		}
	}
	if (d > 0)
	{
		b = b - max_d * eta_d * T_u;
		double res = d - max_d;
		if (res > 0 && z == false)
		{
			max_d_ev = fmin(calc_max_discharging_ev(d, ev_b, min_soc, ev_battery_capacity), alpha_d_ev);
			ev_b = ev_b - max_d_ev * eta_c_ev * T_u;
			res = res - max_d_ev;
		}
		if (res > 0)
		{
			loss_events += 1;
			load_deficit += res;
		}
	}

	return std::make_pair(ev_b, b);
}


std::pair<double, double> mostSustainable(double b, double ev_b, double c, double d, bool z , double max_c, double max_d)
{
	// charge: 1=ev, 2= stationary, 3 = verloren
	double max_c_ev = fmin(calc_max_charging_ev(c, ev_b), alpha_c_ev);
	double max_d_ev;
	//  discharge: 1= stationary, 2 = ev, 3= grid
	if (c > 0)
	{
		ev_b = ev_b + max_c_ev * eta_c_ev * T_u;
		double res = c - max_c_ev;
		if (res > 0)
		{
			max_c = fmin(calc_max_charging(res, b), alpha_c);
			b = b + max_c * eta_c * T_u;
		}
	}
	if (d > 0)
	{
		b = b - max_d * eta_d * T_u;
		double res = d - max_d;
		if (res > 0 && z == false)
		{
			max_d_ev = fmin(calc_max_discharging_ev(d, ev_b, min_soc, ev_battery_capacity), alpha_d_ev);
			ev_b = ev_b - max_d_ev * eta_c_ev * T_u;
			res = res - max_d_ev;
		}
		if (res > 0)
		{
			loss_events += 1;
			load_deficit += res;
		}
	}

	return std::make_pair(ev_b, b);
}

std::tuple<double, double, int> simulateEVCharging(std::vector<EVStatus> &dailyStatuses, int hour, int day, double last_soc)
{
		int selectedEVChargingPolicy = 2;
		double ev_b = 0.0;

		if (!dailyStatuses[hour - 1].isAtHome && dailyStatuses[hour].isAtHome && hour != 0)
		{
			ev_b = dailyStatuses[hour].currentSOC;
		} else {
			ev_b = last_soc;
		}

		int chargeHour = -1;
		// Determine if we should charge this hour
		 if (selectedEVChargingPolicy == 1){
			chargeHour = lastp(dailyStatuses, ev_b, hour);
		}
		else if (selectedEVChargingPolicy == 0){
			 chargeHour = naive(dailyStatuses, ev_b, hour);
		}  else if (selectedEVChargingPolicy == 2){
			 chargeHour = mincost(dailyStatuses, ev_b, hour, t_ch);
		} else {
			std::cout << "ERROR: Invalid EV charging policy selected" << std::endl;
		}

		double maxCharging = 0.0;
				if (chargeHour == hour)
			{
				double available_power = 7.4;
				maxCharging = calc_max_charging_ev(available_power, ev_b);
			}

		return std::make_tuple(maxCharging, ev_b, chargeHour);
}

// call it with a specific battery and PV size and want to compute the loss
double sim(vector<double> &load_trace, vector<double> &solar_trace, int start_index, int end_index, double cells, double pv, double b_0, std::vector<EVRecord> evRecords, std::vector<std::vector<EVStatus>> allDailyStatuses)
{

	update_parameters(cells);

	// set the battery
	double b = b_0*cells*kWh_in_one_cell; //0.5*a2_intercept
	 loss_events = 0;
	 load_deficit = 0;
	 load_sum = 0;



	int trace_length_solar = solar_trace.size();
	int trace_length_load = load_trace.size();

	double c = 0.0;
	double d = 0.0;
	double max_c = 0.0;
	double max_d = 0.0;
	double max_c_ev = 0.0;
	double max_d_ev = 0.0;
	int index_t_solar;
	int index_t_load;
	double last_soc = 32.0;
	int day = 0;
	int hour = 0;
	
	// loop through each hour 
	for (int t = start_index; t < end_index; t++) {
		bool z = false;

		// wrap around to the start of the trace if we hit the end.
		index_t_solar = t % trace_length_solar;
		index_t_load = t % trace_length_load;

		load_sum += load_trace[index_t_load];

		int index = t - start_index;
		hour = index % 24;
		day =  index / 24;
		int day2 = day +1;

		//EV CHARGING 
		// this function should return if we need charging and if yes how much and what the ev state is (last soc)

		std::tuple<double, double, int> chargingResult = simulateEVCharging(allDailyStatuses[day], hour, day, last_soc);
		double maxCharging = std::get<0>(chargingResult);
		double ev_b = std::get<1>(chargingResult);
		int chargingHour = std::get<2>(chargingResult);

		if(chargingHour == hour){
			z = true;
		}

		double hourly_laod = load_trace[index_t_load] + maxCharging;
		//double hourly_laod = load_trace[index_t_load] ;

		// how much charging or discharging would be needed
		c = fmax(solar_trace[index_t_solar]*pv - hourly_laod,0);
		d = fmax(hourly_laod- solar_trace[index_t_solar]*pv, 0);

		// how much we can charge or discharge the battery in reality 
		max_c = fmin(calc_max_charging(c,b), alpha_c);
		max_d = fmin(calc_max_discharging(d,b), alpha_d);
	
		std::pair<double, double> operationResult = unidirectional(b, ev_b, c, d, z, max_c, max_d);
		//std::pair<double, double> operationResult = minstorage(b, ev_b, c, d, z, max_c, max_d);
		//std::pair<double, double> operationResult = rDegradation(b, ev_b, c, d, z, max_c, max_d);
		//std::pair<double, double> operationResult = mostSustainable(b, ev_b, c, d, z, max_c, max_d);

		ev_b = operationResult.first;
		b = operationResult.second;
		// Update current SOC in EVStatus and carry over to next hour
		allDailyStatuses[day][hour].currentSOC = ev_b;
		last_soc = ev_b;

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
