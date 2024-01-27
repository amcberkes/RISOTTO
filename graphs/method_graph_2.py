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

# Define the solar generation data provided by the user (in Wh)
solar_generation_data = [
    0.0, 2.5, 5.0, 8.0, 10.0, 12.0, 15.0, 14.5, 12.0, 9.0, 6.0, 3.0,
    1.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

# Define the hours of the day
hours = np.arange(24)

# Create the area plot with vivid colors
fig, ax = plt.subplots()

# Correct the energy use curve to ensure it reaches the value 24 on the x-axis
corrected_energy_use_two_peaks = np.array(energy_use_two_peaks)[:24]  # Truncate to 24 elements
orrected_soalr = np.array(solar_generation_data)[:24] 

# Define the extended hours to include 24
extended_hours = np.append(hours, 24)
vivid_orange = sns.color_palette("rocket")[4]  # Vivid orange for solar
vivid_purple = sns.color_palette("rocket")[2]  # Vivid purple for load
# Create the area plot with vivid colors
fig, ax = plt.subplots()
ax.fill_between(extended_hours, corrected_energy_use_two_peaks, color=vivid_purple, alpha=0.3, label="Home energy consumption")
ax.fill_between(extended_hours, orrected_soalr, color=vivid_orange, alpha=0.3, label="Solar energy production")

# Shade the entire x-axis area from 0 to 7 and 16 to 24 in grey to represent "EV at home"
ax.axvspan(0, 7, color='grey', alpha=0.2)
ax.axvspan(16, 24, color='grey', alpha=0.2, label='EV at home')

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
