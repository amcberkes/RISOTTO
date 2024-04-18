import numpy as np
import matplotlib.pyplot as plt

def read_and_process(file_path):
    with open(file_path, 'r') as file:
        # Read all lines and convert them to floats
        data = np.array([float(line.strip()) for line in file.readlines()])
        
    # Calculate total PV generation
    total_pv_generation = np.sum(data)
    
    # Calculate average hourly production
    hourly_averages = [np.mean(data[hour::24]) for hour in range(24)]
    
    return total_pv_generation, hourly_averages

def main():
    lerwick_data, lerwick_hourly = read_and_process('Lerwick_pv.txt')
    weymouth_data, weymouth_hourly = read_and_process('Weymouth_pv.txt')
    
    print(f"Total PV generation for Lerwick: {lerwick_data} kWh")
    print(f"Total PV generation for Weymouth: {weymouth_data} kWh")
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(range(24), lerwick_hourly, label='Lerwick', marker='o')
    plt.plot(range(24), weymouth_hourly, label='Weymouth', marker='o')
    plt.title('Average Hourly PV Production')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Average Production (kWh)')
    plt.xticks(range(24), labels=[f'{hour}:00' for hour in range(24)], rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('average_daily_pv_production.png')
    plt.show()

if __name__ == "__main__":
    main()
