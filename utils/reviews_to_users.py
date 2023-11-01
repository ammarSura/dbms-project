"""
copy reviewer_id and reviewer_name from reviews.csv to users.csv.
"""

import csv

# Input and output file paths
input_file = 'database/reviews.csv'
output_file = 'database/users.csv'

with open(input_file, 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)  # Read the headers

    # Find the index of the 4th and 5th columns
    col4_index = headers.index('reviewer_id')
    col5_index = headers.index('reviewer_name')

    # Create a new list to store the updated rows
    updated_rows = []

    # Iterate over each row in the CSV
    for row in reader:
        # Extract the values from the 4th and 5th columns
        col4_value = row[col4_index]
        col5_value = row[col5_index]

        # Create a new row with the copied values
        updated_row = [col4_value, col5_value]

        # Append the updated row to the list
        updated_rows.append(updated_row)

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)

    # Write the renamed headers to the new CSV file
    writer.writerow(['id', 'name'])

    # Write the updated rows to the new CSV file
    writer.writerows(updated_rows)
