import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set the color palette to "rocket"
sns.set_palette("rocket")

# Define the energy use curve provided by the user
energy_use_two_peaks = [
    0.7, 0.7, 0.7, 0.7, 0.7, 1, 1.2, 1.5, 2.6, 0.7, 0.7, 0.7, 
    0.7, 0.7, 1.6, 3.0, 3.2, 2.5, 2.0, 1.8, 1.6, 1.0, 0.7, 0.7
]

# Define the hours of the day
hours = np.arange(24)

# Define the start, peak, and end times for the solar production
start_time = 7
end_time = 16
new_peak_time = 12  # 12:00 PM

# Find the quadratic coefficients for the solar production
new_rise_x = np.array([start_time, new_peak_time])
new_rise_y = np.array([0, 2.9])
new_fall_x = np.array([new_peak_time, end_time])
new_fall_y = np.array([2.9, 0])
new_rise_coefficients = np.polyfit(new_rise_x, new_rise_y, 2)
new_fall_coefficients = np.polyfit(new_fall_x, new_fall_y, 2)

# Generate the solar production values with the adjusted peak
solar_production_shifted = np.zeros(24)
for hour in hours:
    if hour < new_peak_time:
        solar_production_shifted[int(hour)] = np.polyval(new_rise_coefficients, hour)
    else:
        solar_production_shifted[int(hour)] = np.polyval(new_fall_coefficients, hour)
    solar_production_shifted[int(hour)] = max(solar_production_shifted[int(hour)], 0)

# Create the area plo

# Choose more vivid colors from the "rocket" palette for solar and load curves
vivid_orange = sns.color_palette("rocket")[4]  # Vivid orange for solar
vivid_purple = sns.color_palette("rocket")[2]  # Vivid purple for load

# Correct the energy use curve to ensure it reaches the value 24 on the x-axis
corrected_energy_use_two_peaks = np.append(energy_use_two_peaks, energy_use_two_peaks[0])

# Generate the solar production values with the adjusted peak
corrected_solar_production_shifted = np.append(solar_production_shifted, solar_production_shifted[0])

# Define the extended hours to include 24
extended_hours = np.append(hours, 24)

# Create the area plot with vivid colors
fig, ax = plt.subplots()
ax.fill_between(extended_hours, corrected_energy_use_two_peaks, color=vivid_purple, alpha=0.3, label="Home energy consumption")
ax.fill_between(extended_hours, corrected_solar_production_shifted, color=vivid_orange, alpha=0.3, label="Solar energy production")

# Shade the entire x-axis area from 0 to 24 in grey except for the time between 8 - 17:30, representing "EV at home"
ax.axvspan(0, 8, color='grey', alpha=0.2)
ax.axvspan(17.5, 24, color='grey', alpha=0.2, label='EV at home')

# Move the legend to the upper left corner
ax.legend(loc='upper left')

# Add labels and title
ax.set_xlabel('Hour of the day')
ax.set_ylabel('Solar generation (Wh) & House consumption (kWh)')

# Set x and y-axis limits
plt.xlim(0, 24)
plt.ylim(0, 4)

# Show the plot
plt.show()

