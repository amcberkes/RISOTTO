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
    bool isAtHome;
    std::string nextDepartureTime;
    double currentSOC;
};

// Function declarations

void updateEVStatus(EVStatus &status, const std::string &currentTime);

std::vector<EVRecord> readEVData(const std::string &filename);
void printEVRecords(const std::vector<EVRecord> &evRecords);
std::vector<EVStatus> generateDailyStatus(const std::vector<EVRecord> &dayRecords, double &previousSOC);
int findNumberOfDays(const std::vector<EVRecord> &evRecords);
std::vector<std::vector<EVStatus>> generateAllDailyStatuses(const std::vector<EVRecord> &evRecords);
int convertTimeToHour(const std::string &timeStr);
void printAllEVStatuses(const std::vector<std::vector<EVStatus>> &allDailyStatuses, const std::vector<EVRecord> &evRecords);

#endif // EV_H
