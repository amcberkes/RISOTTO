#include "crow_all.h"

int main()
{
    crow::SimpleApp app;

    // Handle POST requests
    CROW_ROUTE(app, "/receive_json").methods("POST"_method)([](const crow::request &req)
                                                            {
        crow::response res;
        auto json = crow::json::load(req.body);

        if (!json) {
            res.code = 400;
            res.body = "Invalid JSON";
        } else {
            // Accessing simple fields
            std::string latitude = json["latitude"].s();
            std::string longitude = json["longitude"].s();

            // Process additional fields (currently commented out)
            /*
            double max_soc = json["max_soc"].d();
            double min_soc = json["min_soc"].d();
            int ev_battery_capacity = json["ev_battery_capacity"].i();
            int charging_rate = json["charging_rate"].i();
            int soc_lim = json["soc_lim"].i();
            std::string EV_charging = json["EV_charging"].s();
            int unidirectional = json["unidirectional"].i();
            double chargeState = json["chargeState"].d();

            // Accessing nested objects
            auto monthly_electricity_load = json["monthly_electricity_load"];
            int load_jan = monthly_electricity_load["Load_Jan"].i();
            int load_feb = monthly_electricity_load["Load_Feb"].i();
            int load_mar = monthly_electricity_load["Load_Mar"].i();
            int load_apr = monthly_electricity_load["Load_Apr"].i();
            int load_may = monthly_electricity_load["Load_May"].i();
            int load_jun = monthly_electricity_load["Load_Jun"].i();
            int load_jul = monthly_electricity_load["Load_Jul"].i();
            int load_aug = monthly_electricity_load["Load_Aug"].i();
            int load_sep = monthly_electricity_load["Load_Sep"].i();
            int load_oct = monthly_electricity_load["Load_Oct"].i();
            int load_nov = monthly_electricity_load["Load_Nov"].i();
            Çint load_dec = monthly_electricity_load["Load_Dec"].i();

            int PV_cost = json["PV_cost"].i();
            int B_cost = json["B_cost"].i();
            int pv_max = json["pv_max"].i();
            int cells_max = json["cells_max"].i();
            double confidence = json["confidence"].d();
            int days_in_chunk = json["days_in_chunk"].i();
            double epsilon = json["epsilon"].d();
            int metric = json["metric"].i();
            bool merge_trips = json["merge_trips"].b();
            std::string path_to_ev_data = json["path_to_ev_data"].s();

            // Accessing sub-object
            auto ev_generator = json["ev_generator"];
            std::string output = ev_generator["output"].s();
            int days = ev_generator["days"].i();
            bool ev_gen_merge_trips = ev_generator["merge_trips"].b();
            int ev_battery = ev_generator["ev_battery"].i();
            int ev_consumption = ev_generator["ev_consumption"].i();
            bool wfh_monday = ev_generator["wfh_monday"].b();
            // ... Additional weekdays ...
            int C_distance = ev_generator["C_distance"].i();
            double C_dept = ev_generator["C_dept"].d();
            double C_arr = ev_generator["C_arr"].d();
            int N_nc = ev_generator["N_nc"].i();
            */

            // Indicate success
            res.body = "JSON received and processed successfully";
        }

        // Add CORS headers
        res.add_header("Access-Control-Allow-Origin", "*");
        res.add_header("Access-Control-Allow-Methods", "POST, OPTIONS");
        res.add_header("Access-Control-Allow-Headers", "Content-Type");
        res.code = 200;
        return res; });

    // Handle OPTIONS for preflight
    CROW_ROUTE(app, "/receive_json").methods("OPTIONS"_method)([](const crow::request &req)
                                                               {
        crow::response res;
        res.code = 204; // No Content
        res.add_header("Access-Control-Allow-Origin", "http://localhost:3000");
        res.add_header("Access-Control-Allow-Methods", "POST, OPTIONS");
        res.add_header("Access-Control-Allow-Headers", "Content-Type");
        return res; });

    app.port(18080).multithreaded().run();
}
