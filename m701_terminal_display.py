import serial
import time
import curses

thresholds = {'eCO2': 4000, 'eCH2O': 15, 'TVOC': 20, 'PM2.5': 50, 'PM10': 70, 'Temperature': 25, 'Humidity': 35}

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

def display_data(window, data):
    window.clear()
    for i, (key, value) in enumerate(data.items()):
        window.addstr(i, 0, f'{key}: {value}')
        if value > thresholds[key]:
            window.addstr(len(data), 0, f'警告：{key}数值超过阈值！')
    window.refresh()

def set_threshold(window):
    global thresholds
    keys = list(thresholds.keys())
    current = 0
    while True:
        window.clear()
        for i, key in enumerate(keys):
            if i == current:
                window.addstr(i, 0, f'{key}: {thresholds[key]}', curses.A_REVERSE)
            else:
                window.addstr(i, 0, f'{key}: {thresholds[key]}')
        window.refresh()
        c = window.getch()
        if c == curses.KEY_UP:
            current = (current - 1) % len(keys)
        elif c == curses.KEY_DOWN:
            current = (current + 1) % len(keys)
        elif c == ord('\n'):
            window.addstr(len(keys), 0, '输入新的阈值：')
            window.refresh()
            curses.echo()
            thresholds[keys[current]] = int(window.getstr(len(keys), 0))
            curses.noecho()
            break

def main():
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)
    window = curses.initscr()
    curses.noecho()
    window.keypad(True)
    while True:
        data = read_m701_data(serial_port)
        if data is not None:
            display_data(window, data)
        c = window.getch()
        if c == ord('i'):
            set_threshold(window)
    curses.endwin()


if __name__ == '__main__':
    main()
