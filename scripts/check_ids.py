import csv

csv1_file_path = 'database/hosts.csv'
csv2_file_path = 'database/listings.csv'
csv1_id_column = 'id'
csv2_id_column = 'host_id'

# Read the IDs from CSV1 into a set
csv1_ids = set()
with open(csv1_file_path, 'r') as csv1_file:
    csv1_reader = csv.reader(csv1_file)
    header_row = next(csv1_reader)  # Skip the header row
    id_index = header_row.index(csv1_id_column)
    for row in csv1_reader:
        csv1_ids.add(row[id_index])
ctr = 0
# Check if any ID in CSV2 is not in CSV1
with open(csv2_file_path, 'r') as csv2_file:
    csv2_reader = csv.reader(csv2_file)
    header_row = next(csv2_reader)  # Skip the header row
    id_index = header_row.index(csv2_id_column)
    for row in csv2_reader:
        if row[id_index] not in csv1_ids:
            ctr += 1
            print(f"ID {row[id_index]} in CSV2 is not present in CSV1")


print(f'ID check complete! ctr: {ctr}')


# import csv

# csv1_file_path = 'database/users.csv'
# csv2_file_path = 'database/listings.csv'
# csv1_id_column = 'id'
# csv2_id_column = 'id'

# # Read the IDs from CSV1 into a set
# csv1_ids = set()
# with open(csv1_file_path, 'r') as csv1_file:
#     csv1_reader = csv.reader(csv1_file)
#     header_row = next(csv1_reader)  # Skip the header row
#     id_index = header_row.index(csv1_id_column)
#     for row in csv1_reader:
#         csv1_ids.add(row[id_index])

# # Remove rows from CSV2 that have IDs not present in CSV1
# filtered_rows = []
# with open(csv2_file_path, 'r') as csv2_file:
#     csv2_reader = csv.reader(csv2_file)
#     header_row = next(csv2_reader)  # Skip the header row
#     id_index = header_row.index(csv2_id_column)
#     for row in csv2_reader:
#         if row[id_index] in csv1_ids:
#             filtered_rows.append(row)

# # Write the filtered rows back to CSV2
# with open(csv2_file_path, 'w', newline='') as csv2_file:
#     csv2_writer = csv.writer(csv2_file)
#     csv2_writer.writerow(header_row)
#     csv2_writer.writerows(filtered_rows)

# print('Rows removed successfully!')

226250
223950
2300
