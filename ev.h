// ev.h
#ifndef EV_H
#define EV_H

#include <string>
#include <vector>


struct EVRecord
{
    int day;
    std::string weekday;
    std::string departureTime;
    double socOnDeparture;
    std::string arrivalTime;
    double socOnArrival;
    double distanceKm;
    int travelTimeMin;
    std::string nextDepartureTime; 
};

extern std::vector<EVRecord> evRecords;


struct EVStatus
{
    int dayNumber;       // New field for day number
    std::string dayName; // New field for day name
    int hour;            // New field for hour
    bool isAtHome;
    std::string nextDepartureTime;
    double currentSOC;
};

// Function declarations

std::vector<EVRecord> readEVData(const std::string &filename);
void printEVRecords(const std::vector<EVRecord> &evRecords);
std::vector<EVStatus> generateDailyStatus(const std::vector<EVRecord> &dayRecords, double &previousSOC);
std::vector<std::vector<EVStatus>> generateAllDailyStatuses(const std::vector<EVRecord> &evRecords);
int convertTimeToHour(const std::string &timeStr);
void printAllEVStatuses(const std::vector<std::vector<EVStatus>> &allDailyStatuses, const std::vector<EVRecord> &evRecords);
void printAllEVStatusesToCSV(const std::vector<std::vector<EVStatus>> &allDailyStatuses, const std::vector<EVRecord> &evRecords, const std::string &filename);

#endif // EV_H
