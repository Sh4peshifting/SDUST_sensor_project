import serial
import time
import curses


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

def create_curses_gui():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    return stdscr

def update_curses_gui(stdscr, data):
    stdscr.clear()
    for i, (key, value) in enumerate(data.items()):
        stdscr.addstr(i, 0, f"{key}: {value}")
    stdscr.refresh()

def check_curses_thresholds(stdscr, data, thresholds):
    warnings = []
    for key, value in data.items():
        if key in thresholds and value > thresholds[key]:
            warnings.append(f"{key}数值超过阈值")
    if warnings:
        stdscr.addstr(len(data), 0, f"警告：{'，'.join(warnings)}")
    stdscr.refresh()

def input_thresholds(stdscr, data):
    thresholds = {}
    stdscr.clear()
    for i, key in enumerate(data.keys()):
        stdscr.addstr(i, 0, f"输入{key}的阈值：")
        curses.echo()
        thresholds[key] = float(stdscr.getstr(i, len(f"输入{key}的阈值：")).decode())
        curses.noecho()
    return thresholds

def main():
    serial_port = serial.Serial('/dev/ttyS4', 9600, timeout=1)
    stdscr = create_curses_gui()
    thresholds = {}
    try:
        while True:
            data = read_m701_data(serial_port)
            if data:
                update_curses_gui(stdscr, data)
                check_curses_thresholds(stdscr, data, thresholds)
            if stdscr.getch() == ord('i'):
                thresholds = input_thresholds(stdscr, data)
            time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()



if __name__ == '__main__':
    main()
