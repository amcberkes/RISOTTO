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
#include <nlohmann/json.hpp>

#include "common.h"

using json = nlohmann::json;

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



        vector<double>
            socValues;

// Callback function to receive data from libcurl
size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// Function to fetch solar data from API, accepting lat and lon as strings
void fetch_solar_data_from_api(const std::string &lat, const std::string &lon, const std::string &outputFilePath, int us)
{
    CURL *curl;
    CURLcode res;
    std::string readBuffer;
    std::vector<double> solar_data;
    cout << "lon: " << lon << endl;
    cout << "lat: " << lat << endl;

    // Initialize CURL
    curl = curl_easy_init();
    std::string url;
    if (curl)
    {
        // Prepare the URL for international
        if(us == 0){
            url = "https://developer.nrel.gov/api/pvwatts/v8.json?api_key=AQApgpuyM8tcFqhfwGyrXKJKQQofUlUt1bGfj9ke"
                              "&azimuth=180&system_capacity=4&losses=14&array_type=1&module_type=0&tilt=10&dataset=intl&timeframe=hourly"
                              "&lat=" +
                              lat + "&lon=" + lon;
        } if(us==1){
            //us
            url = "https://developer.nrel.gov/api/pvwatts/v8.json?api_key=AQApgpuyM8tcFqhfwGyrXKJKQQofUlUt1bGfj9ke"
                              "&azimuth=180&system_capacity=4&losses=14&array_type=1&module_type=0&tilt=10&timeframe=hourly"
                              "&lat=" +
                              lat + "&lon=" + lon;
        }
        


        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        res = curl_easy_perform(curl);
        if (res != CURLE_OK)
        {
            std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
        }
        else
        {
            curl_easy_cleanup(curl);

            // Parse JSON and process
            json j = json::parse(readBuffer);

            // Open a file stream to write the JSON data
            std::ofstream jsonFile("json_interm.txt");
            if (jsonFile.is_open())
            {
                // Write prettified JSON to file with indent of 4 spaces
                jsonFile << j.dump(4);
                jsonFile.close();
                std::cout << "JSON data written to: "
                          << "json_interm.txt" << std::endl;
            }
            else
            {
                std::cerr << "Failed to open file for output: "
                          << "json_interm.txt" << std::endl;
            }

            double system_capacity;
            std::string system_capacity_str = j["inputs"]["system_capacity"].get<std::string>();
            try
            {
                system_capacity = std::stod(system_capacity_str);
            }
            catch (const std::invalid_argument &ia)
            {
                std::cerr << "Invalid argument: " << ia.what() << std::endl;
                return;
            }
            std::vector<double> ac_values = j["outputs"]["ac"].get<std::vector<double>>();
    

            std::ofstream outFile(outputFilePath);
            if (outFile.is_open())
            {
                for (double ac : ac_values)
                {
                    double converted_value = (ac / system_capacity) / 1000; // Converting to kW
                    outFile << converted_value << std::endl;
                }
                outFile.close();
                std::cout << "Processed AC data written to " << outputFilePath << std::endl;
            }
            else
            {
                std::cerr << "Unable to open file for writing: " << outputFilePath << std::endl;
            }
        }
    }
}

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

    // if solarfile is "pvwatts", call pvwatts api 
    if (solarfile == string("pvwatts")) {
        string us_string = argv[++i];
        int us = stod(us_string);
       

        string lat_string = argv[++i];
        lat = stod(lat_string);

        #ifdef DEBUG
        cout << "lat_string = " << lat_string << " , lat= " << lat << endl;
        #endif
        string lon_string = argv[++i];
        lon = stod(lon_string);

        #ifdef DEBUG
        cout << "lon_string = " << lon_string << ", lon = " << lon << endl;
        #endif
        fetch_solar_data_from_api(lat_string, lon_string, "json_pvwatts.txt", us);
        solarfile = "json_pvwatts.txt";
        ifstream solarstream(solarfile.c_str());
        solar = read_data_from_file(solarstream);
    } 

    else if(solarfile == string("--")) {
        // read from cin
        int limit = stoi(argv[++i]);
        solar = read_data_from_file(cin, limit);
    } else {
        // read in data into vector
        ifstream solarstream(solarfile.c_str());
        solar = read_data_from_file(solarstream);
    }

	if (solar[0] < 0) {
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
