import logging
from flask import Flask, request, jsonify, send_file, render_template
import subprocess
import json
import csv, io, requests
from urllib.parse import quote_plus
from io import BytesIO, StringIO  # Import BytesIO and StringIO

app = Flask(__name__)
app.debug = True

logging.basicConfig(filename='log/app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# trim whitespace in the csv
class TrimmedDictReader(csv.DictReader):
    def __next__(self):
        row = super().__next__()
        return {key.strip(): value.strip() for key, value in row.items()}

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/geocode', methods=['GET'])
def geocode():
    address = request.args.get('address')
    if not address:
        app.logger.error('Address parameter is required')
        return jsonify({'error': 'Address parameter is required'}), 400

    app.logger.info(f'Geocoding address: {address}')
    result = subprocess.run(['ruby', '/app/geocode.rb', address], capture_output=True, text=True)
    if result.returncode != 0:
        app.logger.error('Geocoding failed')
        return jsonify({'error': 'Geocoding failed'}), 500

    app.logger.info('Geocoding successful')
    return jsonify(json.loads(result.stdout))

@app.route('/geocode_csv', methods=['GET', 'POST'])
def geocode_csv():
    geocoded_data = []
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if not file.filename.lower().endswith('.csv'):
            return "File is not a CSV", 400

        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = TrimmedDictReader(stream)
        # app.logger.debug(csv_input)

        # Strip whitespace from field names
        fieldnames = [name.strip().lower() for name in csv_input.fieldnames]
        # app.logger.info(f'CSV field names: {fieldnames}')

        # Validate CSV columns
        if 'id' not in fieldnames or 'address' not in fieldnames:
            return "CSV contain 'ID' and 'address' columns", 400

        # Define new fields
        new_fields = ['city', 'fips_county', 'lat', 'lon', 'number', 'precision', 'prenum', 'score', 'state', 'street', 'zip', 'geocode_failed']
        output = StringIO()  # Use StringIO for text data
        csv_output = csv.DictWriter(output, fieldnames=fieldnames + new_fields)
        csv_output.writeheader()

        for row in csv_input:
            app.logger.debug(row)
            address = row.get('address')
            if address:
                encoded_address = quote_plus(address)
                response = requests.get(f"http://localhost:9080/geocode?address={encoded_address}")
                if response.status_code == 200:
                    geocode_data = response.json()[0]
                    row.update(geocode_data)
                    row['geocode_failed'] = 'False'
                    geocoded_data.append({
                        'id': row['id'],
                        'lat': geocode_data.get('lat'),
                        'lon': geocode_data.get('lon')
                    })
                else:
                    for field in new_fields[:-1]:  # Exclude 'geocode_failed' from blank fields
                        row[field] = ''
                    row['geocode_failed'] = 'True'
                
                # Ensure row only contains keys in fieldnames
                filtered_row = {key: row[key] for key in csv_output.fieldnames if key in row}
                csv_output.writerow(filtered_row)
            else:
                app.logger.error("Address key is missing in the row")

        # Encode the StringIO data to bytes
        output.seek(0)
        byte_output = BytesIO(output.getvalue().encode('utf-8'))

        return send_file(byte_output, mimetype='text/csv', download_name='geocoded.csv', as_attachment=True)

    # Render the upload form with geocoded data
    return render_template('upload.html', geocoded_data=geocoded_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, threaded=True)