import serial
import time
from flask import Flask, render_template, request

app = Flask(__name__)

# Global variable to store the data
data = {}

# Threshold values
thresholds = {'eCO2': 1000, 'eCH2O': 0.1, 'TVOC': 0.5, 'PM2.5': 35, 'PM10': 50, 'Temperature': 30, 'Humidity': 60}

def read_m701_data(serial_port):
    # Read response
    response = serial_port.read(17)

    # Verify frame header
    if response[0] != 0x3C or response[1] != 0x02:
        print("Invalid frame header")
        return None

    # Parse response
    data = {'eCO2': int.from_bytes(response[2:4], byteorder='big'),
            'eCH2O': int.from_bytes(response[4:6], byteorder='big'),
            'TVOC': int.from_bytes(response[6:8], byteorder='big'),
            'PM2.5': int.from_bytes(response[8:10], byteorder='big'),
            'PM10': int.from_bytes(response[10:12], byteorder='big'), 'Temperature': response[12] + response[13] / 10,
            'Humidity': response[14] + response[15] / 10}

    # Verify checksum
    checksum = sum(response[:-1]) & 0xFF
    if checksum != response[-1]:
        print("Invalid checksum")
        return None

    return data

@app.route('/', methods=['GET', 'POST'])
def home():
    global thresholds
    if request.method == 'POST':
        # Update thresholds
        for key in thresholds.keys():
            thresholds[key] = float(request.form[key])
    # Get warnings
    warnings = {key: value > thresholds[key] for key, value in data.items()}
    return render_template('home.html', data=data, warnings=warnings, thresholds=thresholds)

def main():
    # Configure serial port
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)

    while True:
        try:
            data = read_m701_data(serial_port)
            if data:
                print(data)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
    app.run(debug=True)
