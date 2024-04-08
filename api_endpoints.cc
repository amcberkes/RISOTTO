#include <pistache/endpoint.h>
#include <nlohmann/json.hpp>
#include <iostream>

using json = nlohmann::json;
using namespace Pistache;

// Define a function to handle the POST request
void handlePostData(const Rest::Request &request, Http::ResponseWriter response)
{
    try
    {
        // Parse the request body into a json object
        auto j = json::parse(request.body());

        // Example of accessing various fields
        std::string latitude = j["latitude"];
        std::string longitude = j["longitude"];
        double max_soc = j["max_soc"];
        double min_soc = j["min_soc"];
        int ev_battery_capacity = j["ev_battery_capacity"];
        int charging_rate = j["charging_rate"];
        int soc_lim = j["soc_lim"];
        std::string EV_charging = j["EV_charging"];
        int unidirectional = j["unidirectional"];
        double chargeState = j["chargeState"];
        int PV_cost = j["PV_cost"];
        int B_cost = j["B_cost"];
        int pv_max = j["pv_max"];
        int cells_max = j["cells_max"];
        double confidence = j["confidence"];
        int days_in_chunk = j["days_in_chunk"];
        double epsilon = j["epsilon"];
        int metric = j["metric"];
        bool merge_trips = j["merge_trips"];
        std::string path_to_ev_data = j["path_to_ev_data"];

        // Accessing nested JSON object
        auto monthly_electricity_load = j["monthly_electricity_load"];
        int load_jan = monthly_electricity_load["Load_Jan"];
        // Continue for other months...

        // Accessing nested JSON object within an object
        auto ev_generator = j["ev_generator"];
        int days = ev_generator["days"];
        // Continue for other fields in ev_generator...

        // Log to console (for demonstration)
        std::cout << "Latitude: " << latitude << ", Longitude: " << longitude << std::endl;
        // Print more fields as needed...

        // Send a response back
        response.send(Http::Code::Ok, "Data received and processed");
    }
    catch (json::parse_error &e)
    {
        std::cerr << "JSON Parse Error: " << e.what() << std::endl;
        response.send(Http::Code::Bad_Request, "Invalid JSON");
    }
    catch (std::exception &e)
    {
        // Catch any other standard exceptions (e.g., accessing missing fields)
        std::cerr << "Error: " << e.what() << std::endl;
        response.send(Http::Code::Internal_Server_Error, "An error occurred");
    }
}

int main()
{
    // Initialize the HTTP server and router
    Pistache::Port port(8080);
    Pistache::Address addr(Pistache::Ipv4::any(), port);
    auto opts = Pistache::Http::Endpoint::options()
                    .threads(1)
                    .flags(Pistache::Tcp::Options::ReuseAddr);
    Http::Endpoint server(addr);
    server.init(opts);
    Rest::Router router;

    // Bind the handler function to a route
    Pistache::Rest::Routes::Post(router, "/api/sendData", Pistache::Rest::Routes::bind(&handlePostData));

    // Set the router
    server.setHandler(router.handler());

    // Start the server
    server.serve();
}
