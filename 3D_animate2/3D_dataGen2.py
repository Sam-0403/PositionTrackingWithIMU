
import csv
import random
import time

namafile = 'data3D.csv'
header1 = "x_value"
header2 = "y_value"
header3 = "z_value"

x_value = 0
y_value = 1000
z_value = 1000

fieldnames = [header1, header2, header3]


with open(namafile, 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

while True:

    with open(namafile, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        info = {
            header1: x_value,
            header2: y_value,
            header3: z_value
        }

        csv_writer.writerow(info)
        print(x_value, y_value, z_value)

        x_value += 1
        y_value = y_value + random.randint(-6, 8)
        z_value = z_value + random.randint(-5, 6)

    time.sleep(1)
