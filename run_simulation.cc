#include <fstream>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <iostream>
#include <iomanip>
#include <limits>
#include <algorithm>
#include "simulate_system.h"
#include "common.h"
#include "cheby.h"
#include "ev.h"

using namespace std;

// run_simulations
// load_filename: filename, each line in file contains electricity consumption value
// solar_filename: filename, each line in file contains solar generation value
// id: request id
// metric: 0 for LOLP, 1 for unmet load
// epsilon: number in range [0,1] representing LOLP or unmet load fraction.
// chunk_size: length of time (in days)
SimulationResult run_simulations(vector<double> &load, vector<double> &solar, int metric, int chunk_size, int number_of_chunks, std::vector<EVRecord> evRecords, std::vector<std::vector<EVStatus>> allDailyStatuses) {

	// set random seed to a specific value if you want consistency in results
	srand(10);

	// get number of timeslots in each chunk
	//zb 100 days a 24h if we have hourly data in the input files 
	int t_chunk_size = chunk_size*(24/T_u);

	vector <vector<SimulationResult> > results;

	// get random start times and run simulation on this chunk of data
	// compute all sizing curves
	for (int chunk_num = 0; chunk_num < number_of_chunks; chunk_num += 1) {

		int chunk_start = rand() % max(solar.size(),load.size());
		int chunk_end = chunk_start + t_chunk_size;

		vector <SimulationResult> sr = simulate(load, solar, chunk_start, chunk_end, 0, evRecords, allDailyStatuses);
		//saves the sizing curve for this sample 
		results.push_back(sr);

	}
{

	// set random seed to a specific value if you want consistency in results
	srand(10);

	// get number of timeslots in each chunk
	//zb 100 days a 24h if we have hourly data in the input files 
	int t_chunk_size = chunk_size*(24/T_u);

	vector <vector<SimulationResult> > results;

	// get random start times and run simulation on this chunk of data
	// compute all sizing curves
	for (int chunk_num = 0; chunk_num < number_of_chunks; chunk_num += 1) {

		int chunk_start = rand() % max(solar.size(),load.size());
		int chunk_end = chunk_start + t_chunk_size;

		vector <SimulationResult> sr = simulate(load, solar, chunk_start, chunk_end, 0, evRecords, allDailyStatuses);
		//saves the sizing curve for this sample 
		results.push_back(sr);

	}

#ifdef DEBUG
	// print all of the curves
	int chunk_index = 1;
	cout << "DEBUG: sizing_curves" << endl;
	for (vector<vector<SimulationResult>>::iterator it = results.begin(); it != results.end(); ++it, ++chunk_index) {
		cout << "chunk_" << chunk_index << endl;
		for (vector<SimulationResult>::iterator it2 = it->begin() ; it2 != it->end(); ++it2) {
			cout << it2->B << "\t" << it2->C << "\t" << it2->cost << endl;
		}
	}
	cout << "DEBUG: sizing_curves_end" << endl;
#endif

	// calculate the chebyshev curves, find the cheapest system along their upper envelope, and return it
	// returns the optimal result 
	return calculate_sample_bound(results, epsilon, confidence);
}
}

int main(int argc, char ** argv) 
{

	int input_process_status = process_input(argv, true);

	// Handle input processing error if needed
	if (input_process_status != 0)
	{
		std::cerr << "Error processing input" << std::endl;
		return 1; // Or handle the error as appropriate
	}

	// Read EV data
	std::vector<EVRecord> evRecords = readEVData("ev.csv");

	// Check if EV data was read successfully
	if (evRecords.empty())
	{
		std::cerr << "Error reading EV data or no records found" << std::endl;
		return 1; // Or handle the error as appropriate
	}

	// Initialize EVStatus
	EVStatus evStatus;
	printEVRecords(evRecords);

	// Generate all daily statuses
	std::vector<std::vector<EVStatus>> allDailyStatuses = generateAllDailyStatuses(evRecords);
	//printAllEVStatuses(allDailyStatuses, evRecords);

	SimulationResult sr = run_simulations(load, solar, metric, days_in_chunk, number_of_chunks, evRecords, allDailyStatuses);

	double cost = sr.B / kWh_in_one_cell * B_inv + sr.C * PV_inv;
	cout << "Battery: " << sr.B << "\tPV: " << sr.C << "\tCost: " << cost << endl;

	return 0;
}
