import requests
import csv
import io

# Define the URL for the /geocode_csv route
url = "http://localhost:9080/geocode_csv"

# Define the path to the CSV file with test addresses
csv_file_path = "testing_addresses.csv"

# print the csv to the terminal
with open(csv_file_path, 'r') as f:
    reader = csv.reader(f,skipinitialspace=True)
    for row in reader:
        print(row)

    # # Read the CSV file
    # # stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    # csv_input = csv.DictReader(f)

    # # Validate CSV columns
    # fieldnames = [name.lower() for name in csv_input.fieldnames]
    # print(fieldnames)

# Send a POST request with the CSV file
with open(csv_file_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)

# Check the response status code
if response.status_code == 200:
    # Save the returned CSV file
    with open('geocoded_addresses.csv', 'wb') as f:
        f.write(response.content)
    print("Geocoded CSV file saved as 'geocoded_addresses.csv'.")
else:
    print(f"Failed to get geocoded CSV. Status code: {response.status_code}")
    print(response.text)