"""
Remove duplicate ids
"""
import csv

# Input and output file paths
input_file = 'database/new_users.csv'
output_file = 'database/new_new_users.csv'

# Create a set to store unique IDs
unique_ids = set()

# Create a list to store the updated rows
updated_rows = []

with open(input_file, 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)  # Read the headers

    # Find the index of the id column
    id_index = headers.index('id')

    # Iterate over each row in the CSV
    for row in reader:
        # Extract the id value from the row
        id_value = row[id_index]

        # Check if the id value is already in the set
        if id_value not in unique_ids:
            # Add the id value to the set
            unique_ids.add(id_value)

            # Append the row to the updated rows list
            updated_rows.append(row)

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)

    # Write the headers to the new CSV file
    writer.writerow(headers)

    # Write the updated rows to the new CSV file
    writer.writerows(updated_rows)
