import csv

def time_to_minutes(time_str):
    """Converts a time string in HH:MM format to minutes since midnight."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        # Return a large number to indicate invalid or missing time
        return 24 * 60 

def format_soc(soc_str):
    """Formats SOC string to one decimal precision, handling empty strings."""
    try:
        return '{:.1f}'.format(float(soc_str))
    except ValueError:
        return ''  # Return empty string if soc_str is invalid

def merge_trips(trips):
    merged_trips = []
    for trip in trips:
        trip_list = list(trip)

        if trip_list[2] == "No trips":
            trip_list.extend(["", ""])
            merged_trips.append(trip_list)
            continue

        if len(trip_list) < 8:
            continue

        start_time = time_to_minutes(trip_list[2])
        end_time = time_to_minutes(trip_list[4])
        soc = format_soc(trip_list[5])
        distance = float(trip_list[6]) if trip_list[6] else 0
        travel_time = float(trip_list[7]) if trip_list[7] else 0

        if not merged_trips or merged_trips[-1][2] == "No trips":
            merged_trips.append(trip_list)
        else:
            last_trip = merged_trips[-1]

            if len(last_trip) < 8:
                continue

            last_end_time = time_to_minutes(last_trip[4])
            last_soc = format_soc(last_trip[5])
            last_distance = float(last_trip[6]) if last_trip[6] else 0
            last_travel_time = float(last_trip[7]) if last_trip[7] else 0

            if start_time <= last_end_time:
                new_end_time = max(last_end_time, end_time)
                new_soc = format_soc('{:.1f}'.format(min(float(last_soc) if last_soc else 0, float(soc) if soc else 0)))
                new_distance = last_distance + distance
                new_travel_time = last_travel_time + travel_time
                new_trip = [last_trip[0], last_trip[1], last_trip[2], 
                            format_soc(last_trip[3]), 
                            f"{new_end_time // 60:02d}:{new_end_time % 60:02d}", 
                            new_soc, f"{new_distance:.2f}", f"{new_travel_time:.0f}"]
                merged_trips[-1] = new_trip
            else:
                merged_trips.append(trip_list)

    return merged_trips



def process_file(input_file, output_file):
    with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        headers = next(reader)
        headers.extend(["Distance (km)", "Travel Time (min)"])  
        writer.writerow(headers)

        current_day = None
        current_trips = []

        for row in reader:
            if len(row) < 6:
                continue

            day = int(row[0])
            if day != current_day and current_trips:
                for merged_trip in merge_trips(current_trips):
                    writer.writerow(merged_trip)
                current_trips = []

            current_day = day
            current_trips.append(row)

        for merged_trip in merge_trips(current_trips):
            writer.writerow(merged_trip)

# replace this with the input and output file names
process_file('ev_T3.csv', 'ev_merged_T3.csv')
