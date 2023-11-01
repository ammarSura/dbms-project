import csv

csv_file_path = 'database/listings.csv'
column_name = 'price'

# Open and read the CSV file
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    csv_data = list(csv_reader)

# Find the index of the specified column
header_row = csv_data[0]
column_index = header_row.index(column_name)
l1 = len(csv_data)
# Iterate over each row in the CSV data
for row in csv_data[1:]:
    value = row[column_index]

    if ',' in value:
        row[column_index] = value.replace(',', '')
    else:
        pass

l2 = len(csv_data)
if l1 != l2:
    exit()

# Open the CSV file in write mode
with open('database/new_listings.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the updated data to the CSV file
    csv_writer.writerows(csv_data)

print('CSV file updated successfully!')
