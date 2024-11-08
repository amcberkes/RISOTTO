#include <fstream>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <iostream>
#include <climits>
#include <string>
#include <set>
#include <curl/curl.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include <vector>
#include <string>
#include "common.h"


double B_inv; // cost per cell
double PV_inv; // cost per unit (kW) of PV

double cells_min;
double cells_max;
double cells_step; // search in step of x cells
double pv_min;
double pv_max;
double pv_step; // search in steps of x kW

double max_soc;
double min_soc;

double ev_battery_capacity = 40.0;
double charging_rate = 7.4;
std::string EV_charging;               
std::string Operation_policy; 
std:: string path_to_ev_data ;

double epsilon;
double confidence;
int metric;
int days_in_chunk;

vector<double> load;
vector<double> solar;



vector<double> socValues;

vector<double> read_data_from_file(istream &datafile, int limit = INT_MAX) {

    vector <double> data;

	if (datafile.fail()) {
    	data.push_back(-1);
    	cerr << errno << ": read data file failed." << endl;
    	return data;
  	}

    // read data file into vector
    string line;
    double value;

    for (int i = 0; i < limit && getline(datafile, line); ++i) {
    	istringstream iss(line);
    	iss >> value;
    	data.push_back(value);
    }

    return data;
}

int process_input(char** argv, bool process_metric_input) {

    double lat = 40.753;
    double lon = -73.983;

    // Using stringstream and setprecision to control the number of decimal places
    std::ostringstream lat_ss;
    std::ostringstream lon_ss;

    lat_ss << std::fixed << std::setprecision(3) << lat;
    lon_ss << std::fixed << std::setprecision(3) << lon;

    std::string lat_str = lat_ss.str();
    std::string lon_str = lon_ss.str();

    int i = 0;
    
    string inv_PV_string = argv[++i];
    PV_inv = stod(inv_PV_string);

#ifdef DEBUG
    cout << "inv_PV_string = " << PV_inv
         << ", PV_inv = " << PV_inv << endl;
#endif

    string inv_B_string = argv[++i];
    B_inv = stod(inv_B_string)*kWh_in_one_cell; // convert from per-kWh to per-cell cost

#ifdef DEBUG
    cout << "inv_B_string = " << inv_B_string 
         << ", B_inv = " << B_inv << endl;
#endif

    string pv_max_string = argv[++i];
    pv_max = stod(pv_max_string);

    // set default pv_min and pv_step
    pv_min = 0;
    pv_step = (pv_max - pv_min) / num_pv_steps;

#ifdef DEBUG
    cout << "pv_max_string = " << pv_max_string
         << ", pv_max = " << pv_max
         << ", pv_min = " << pv_min
         << ", pv_step = " << pv_step
         << endl;
#endif

    string cells_max_string = argv[++i];
    cells_max = stod(cells_max_string) / kWh_in_one_cell;

    // set default cells_min and cells_step
    cells_min = 0;
    cells_step = (cells_max - cells_min) / num_cells_steps;

#ifdef DEBUG
    cout << "cells_max_string = " << cells_max_string
         << ", cells_max = " << cells_max
         << ", cells_min = " << cells_min
         << ", cells_step = " << cells_step
         << endl;
#endif

    if (process_metric_input) {
        string metric_string = argv[++i];
        metric = stoi(metric_string);

#ifdef DEBUG
        cout << "metric_string = " << metric_string
            << ", metric = " << metric << endl;
#endif
    }

    string epsilon_string = argv[++i];
    epsilon = stod(epsilon_string);

#ifdef DEBUG
    cout << "epsilon_string = " << epsilon_string
         << ", epsilon = " << epsilon << endl;
#endif

    string confidence_string = argv[++i];
    confidence = stod(confidence_string);

#ifdef DEBUG
    cout << "confidence_string = " << confidence_string
         << ", confidence = " << confidence << endl;
#endif

    string days_in_chunk_string = argv[++i];
    days_in_chunk = stoi(days_in_chunk_string);

#ifdef DEBUG
    cout << "days_in_chunk_string = " << days_in_chunk_string
         << ", days_in_chunk = " << days_in_chunk << endl;
#endif

    string loadfile = argv[++i];

#ifdef DEBUG
    cout << "loadfile = " << loadfile << endl;
#endif

    if (loadfile == string("--")) {
        // read from cin
        int limit = stoi(argv[++i]);

#ifdef DEBUG
        cout << "reading load data from stdin. limit = " << limit << endl;
#endif

        load = read_data_from_file(cin, limit);
    } else {

#ifdef DEBUG
        cout << "reading load file" << endl;
#endif

        // read in data into vector
        ifstream loadstream(loadfile.c_str());
        load = read_data_from_file(loadstream);
    }

#ifdef DEBUG
	cout << "checking for errors in load file..." << endl;
#endif

	if (load[0] < 0) {
		cerr << "error reading load file " << loadfile << endl;
		return 1;
	}

    string solarfile = argv[++i];

#ifdef DEBUG
    cout << "solarfile = " << solarfile << endl;
#endif

    if (solarfile == string("--"))
    {

#ifdef DEBUG
        cout << "reading solar file" << endl;
#endif

        // read from cin
        int limit = stoi(argv[++i]);

#ifdef DEBUG
        cout << "reading solar data from stdin. limit = " << limit << endl;
#endif

        solar = read_data_from_file(cin, limit);
    }
    else
    {
        // read in data into vector
        ifstream solarstream(solarfile.c_str());
        solar = read_data_from_file(solarstream);
    }

#ifdef DEBUG
    cout << "checking for errors in solar file..." << endl;
#endif

    if (solar[0] < 0)
    {
        cerr << "error reading solar file " << solarfile << endl;
        return 1;
    }

    string max_soc_string = argv[++i];
    max_soc = stod(max_soc_string);

#ifdef DEBUG
    cout << "max_soc_string = " << max_soc_string << ", max_soc = " << max_soc << endl;
#endif

    string min_soc_string = argv[++i];
    min_soc = stod(min_soc_string);

#ifdef DEBUG
    cout << "min_soc_string = " << min_soc_string << ", min_soc = " << min_soc << endl;
#endif
    string ev_battery_capacity_string = argv[++i];
    ev_battery_capacity = stod(ev_battery_capacity_string);

#ifdef DEBUG
    cout << "ev_battery_capacity_string = " << ev_battery_capacity_string << ", ev_battery_capacity = " << ev_battery_capacity << endl;
#endif
  
    string charging_rate_string = argv[++i];
    charging_rate = stod(charging_rate_string);

#ifdef DEBUG
    cout << "charging_rate_string = " << charging_rate_string << ", charging_rate = " << charging_rate << endl;
#endif

    std::set<std::string> validOperationPolicyOptions = {"optimal_unidirectional", "safe_unidirectional", "hybrid_unidirectional", "optimal_bidirectional", "hybrid_bidirectional", "safe_bidirectional", "hybrid_bidirectional"};

       
    std::string operationPolicyInput = argv[++i]; 

    

    if (validOperationPolicyOptions.find(operationPolicyInput) == validOperationPolicyOptions.end())
    {
        std::cerr << "Invalid Operation policy: " << operationPolicyInput << std::endl;
        exit(EXIT_FAILURE); 
    }

    Operation_policy = operationPolicyInput;

    string path_to_ev_data_string = argv[++i];
    path_to_ev_data = path_to_ev_data_string;
   

#ifdef DEBUG
    cout << " path_to_ev_data = " << path_to_ev_data << endl;
#endif



    return 0;
}
