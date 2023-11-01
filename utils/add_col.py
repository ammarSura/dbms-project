import csv
import hashlib

csv_file_path = 'database/users.csv'
new_column_name = 'email'
new_column_value = "admin@gmail.com"
# Open and read the CSV file
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    csv_data = list(csv_reader)

# Add the new column header to the header row
header_row = csv_data[0]
header_row.append(new_column_name)

# Add the new column value to each row
ctr = 1
for row in csv_data[1:]:
    row.append(new_column_value[0:5]+f"{ctr}"+new_column_value[5:])
    ctr += 1

# Open the CSV file in write mode
with open("database/new_users.csv", 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the updated data to the CSV file
    csv_writer.writerows(csv_data)

print('CSV file updated successfully!')
