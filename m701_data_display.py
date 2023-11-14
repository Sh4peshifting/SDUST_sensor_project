import serial
import time
import tkinter as tk


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
            'PM10': int.from_bytes(response[10:12], byteorder='big'), 
            'Temperature': response[12] + response[13] / 10,
            'Humidity': response[14] + response[15] / 10}

    # Verify checksum
    checksum = sum(response[:-1]) & 0xFF
    if checksum != response[-1]:
        print("Invalid checksum")
        return None

    return data

def create_gui():
    window = tk.Tk()
    window.title("传感器数据")
    labels = ['eCO2含量', 'eCH2O含量', 'TVOC含量', 'PM2.5含量', 'PM10含量', '温度', '湿度']
    for i, label in enumerate(labels):
        tk.Label(window, text=f"{label}：").grid(row=i, column=0)
        tk.Label(window, text="设定阈值：").grid(row=i, column=2)
        tk.Entry(window).grid(row=i, column=1)  # Data display
        tk.Entry(window).grid(row=i, column=3)  # Threshold input
    tk.Label(window, text="警告：").grid(row=8, column=0)
    return window

def update_gui(window, data):
    for i, value in enumerate(data.values()):
        window.grid_slaves(row=i, column=1)[0].delete(0, tk.END)
        window.grid_slaves(row=i, column=1)[0].insert(0, str(value))

def check_thresholds(window, data):
    warnings = []
    for i, (key, value) in enumerate(data.items()):
        threshold = window.grid_slaves(row=i, column=3)[0].get()
        if threshold and value > float(threshold):
            warnings.append(f"{key}数值超过阈值")
    window.grid_slaves(row=8, column=0)[0].config(text=f"警告：{'，'.join(warnings)}")

def main():
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)
    window = create_gui()
    while True:
        try:
            data = read_m701_data(serial_port)
            if data:
                update_gui(window, data)
                check_thresholds(window, data)
            window.update()
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == '__main__':
    main()
