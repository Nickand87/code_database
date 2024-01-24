import csv
import os

# Define the input and output paths
input_file_path = 'Unprocessed/Parse_Original.txt'
output_file_path = 'Processed/parsed_data.csv'

# Make sure the 'Processed' directory exists
os.makedirs('Processed', exist_ok=True)

# Read the file and parse the lines
with open(input_file_path, 'r') as file:
    lines = file.readlines()

# Extracting game names and product codes
games_and_codes = [(lines[i].strip(), lines[i+4].strip()) for i in range(0, len(lines), 9) if i+4 < len(lines)]

# Write to CSV
with open(output_file_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the headers
    csvwriter.writerow(['Product Name', 'Product Code', 'Product Code Type', 'Status'])
    # Write the data
    for game, code in games_and_codes:
        csvwriter.writerow([game, code, 'Unknown', 'Unknown'])

print(f"Data has been processed and saved to {output_file_path}")