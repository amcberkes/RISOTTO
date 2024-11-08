import csv

def remove_quotes(input_file, output_file):
    with open(input_file, 'r') as file:
        # Read the CSV file content
        content = file.read()
        
    # Remove every occurrence of the " character
    modified_content = content.replace('"', '')
    
    # Write the modified content to the output file
    with open(output_file, 'w') as file:
        file.write(modified_content)

# Example usage
input_file = 'pvwatts_hourly.csv'  # Replace with your input file name
output_file = 'pvwatts_hourly_2.csv'  # Specify the output file name
remove_quotes(input_file, output_file)
