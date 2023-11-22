import serial
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variable to store the data
data = {'CO2(ppm):': 0, 'CH2O(ug/m3):': 0, 'TVOC(ug/m3):': 0, 'PM2.5(ug/m3):': 0, 'PM10(ug/m3):': 0, '温度(℃):': 0, '湿度(%):': 0}
warnings = {}

# Threshold values
thresholds = {'CO2(ppm):': 1000, 'CH2O(ug/m3):': 0.1, 'TVOC(ug/m3):': 0.5, 'PM2.5(ug/m3):': 35, 'PM10(ug/m3):': 50, '温度(℃):': 30, '湿度(%):': 60}

def read_m701_data(serial_port):
    global data

    # Read response
    response = serial_port.read(17)

    # Check if the response has the expected length
    if len(response) != 17:
        print("Invalid response length")
        return data

    # Verify frame header
    if response[0] != 0x3C or response[1] != 0x02:
        print("Invalid frame header")
        return None
    
    # Parse response
    data = {'CO2(ppm):': int.from_bytes(response[2:4], byteorder='big'),
            'CH2O(ug/m3):': int.from_bytes(response[4:6], byteorder='big'),
            'TVOC(ug/m3):': int.from_bytes(response[6:8], byteorder='big'),
            'PM2.5(ug/m3):': int.from_bytes(response[8:10], byteorder='big'),
            'PM10(ug/m3):': int.from_bytes(response[10:12], byteorder='big'), '温度(℃):': response[12] + response[13] / 10,
            '湿度(%):': response[14] + response[15] / 10}

    # Verify checksum
    checksum = sum(response[:-1]) & 0xFF
    if checksum != response[-1]:
        print("Invalid checksum")
        return None

    return data

def read_data():
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)
    while True:
        global data
        data = read_m701_data(serial_port)

@app.route('/data', methods=['GET'])
def get_data():
    global data, warnings
    return jsonify(data=data, warnings=warnings)

@app.route('/', methods=['GET', 'POST'])
def home():
    global thresholds, warnings
    if request.method == 'POST':
        # Update thresholds
        for key in thresholds.keys():
            thresholds[key] = float(request.form[key])
    # Get warnings
    warnings = {key: value > thresholds[key] for key, value in data.items()}
    return render_template('home.html', data=data, warnings=warnings, thresholds=thresholds)

if __name__ == '__main__':
    # Start a new thread for data reading
    threading.Thread(target=read_data).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
