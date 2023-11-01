import csv

csv1_file_path = 'database/users.csv'
csv2_file_path = 'database/hosts.csv'

# Read the data from CSV1 into a dictionary
csv1_data = {}
with open(csv1_file_path, 'r') as csv1_file:
    csv1_reader = csv.reader(csv1_file)
    hr1 = next(csv1_reader)  # Skip the header row
    id_index = hr1.index('id')
    for row in csv1_reader:
        csv1_data[row[id_index]] = row

# Update CSV1 with the data from CSV2
with open(csv2_file_path, 'r') as csv2_file:
    csv2_reader = csv.reader(csv2_file)
    hr2 = next(csv2_reader)  # Skip the header row
    id_index = hr2.index('id')
    picture_url_index = hr2.index('picture_url')
    for row in csv2_reader:
        id_value = row[id_index]
        picture_url_value = row[picture_url_index]

        if id_value in csv1_data:
            csv1_data[id_value][hr2.index('is_host')] = 't'
            csv1_data[id_value][hr2.index(
                'picture_url')] = picture_url_value
        else:
            new_row = [id_value, row[hr2.index(
                'name')], 't', picture_url_value]
            csv1_data[id_value] = new_row

# Write the updated data
with open("database/new_users.csv", 'w', newline='') as csv1_file:
    csv1_writer = csv.writer(csv1_file)
    csv1_writer.writerow(hr2)
    csv1_writer.writerows(csv1_data.values())

print('CSV3 created successfully!')
