import csv

csv_file_path = 'database/listings.csv'
latitude_column = 'latitude'
longitude_column = 'longitude'
coordinate_column = 'coord'

# Open and read the CSV file
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    csv_data = list(csv_reader)

# Find the indices of the latitude and longitude columns
header_row = csv_data[0]
latitude_index = header_row.index(latitude_column)
longitude_index = header_row.index(longitude_column)

# Iterate over each row in the CSV data
for row in csv_data[1:]:
    latitude = row[latitude_index]
    longitude = row[longitude_index]
    coordinate = f"({longitude}, {latitude})"
    row.append(coordinate)

# Open the CSV file in write mode
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the updated data to the CSV file
    csv_writer.writerows(csv_data)

print('CSV file updated successfully!')
