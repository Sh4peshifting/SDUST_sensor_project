import serial
import time
import requests


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


def send_data_to_server(data, server_url):
    try:
        response = requests.post(server_url, json=data)
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print(f"Error sending data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending data: {e}")


def main():
    # Configure serial port
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)

    # Set server URL
    server_url = "http://127.0.0.1:8080"

    while True:
        try:
            data = read_m701_data(serial_port)
            if data:
                print(data)
                send_data_to_server(data, server_url)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == '__main__':
    main()
