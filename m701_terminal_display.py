import serial
import time
import curses

# 初始化串口
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# 初始化阈值
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

def display_data(stdscr, data):
    stdscr.clear()
    stdscr.addstr(0, 0, "CO2含量: {} ppm".format(data['eCO2']))
    stdscr.addstr(1, 0, "CH2O含量: {} ug/m3".format(data['eCH2O']))
    stdscr.addstr(2, 0, "TVOC含量: {} ug/m3".format(data['TVOC']))
    stdscr.addstr(3, 0, "PM2.5含量: {} ug/m3".format(data['PM2.5']))
    stdscr.addstr(4, 0, "PM10含量: {} ug/m3".format(data['PM10']))
    stdscr.addstr(5, 0, "温度: {} ℃".format(data['Temperature']))
    stdscr.addstr(6, 0, "湿度: {} %".format(data['Humidity']))
    for i, (key, value) in enumerate(data.items()):
        if value > thresholds[key]:
            stdscr.addstr(7, 0, f'警告：{key}数值超过阈值！')
    stdscr.refresh()

def handle_input(stdscr, data):
    c = stdscr.getch()
    if c == ord('i'):
        # 暂停数据接收，设置阈值
        selected = 0
        while True:
            for i, key in enumerate(data.keys()):
                if i == selected:
                    stdscr.addstr(i, 0, "{}: {} (按回车设置阈值)".format(key, data[key]), curses.A_REVERSE)
                else:
                    stdscr.addstr(i, 0, "{}: {} (按回车设置阈值)".format(key, data[key]))
            stdscr.refresh()
            c = stdscr.getch()
            if c == curses.KEY_UP:
                selected = (selected - 1) % len(data)
            elif c == curses.KEY_DOWN:
                selected = (selected + 1) % len(data)
            elif c == curses.KEY_ENTER or c == 10 or c == 13:
                for key in data.keys():
                    if key == list(data.keys())[selected]:
                        stdscr.addstr(i, 0, "{} 阈值: ".format(key))
                        stdscr.refresh()
                        threshold = stdscr.getstr()
                        thresholds[key] = int(threshold)
                        break
                break

def main(stdscr):
    while True:
        # 读取串口数据
        data = read_m701_data(ser)
        # 显示数据
        display_data(stdscr, data)
        # 处理键盘输入
        handle_input(stdscr, data)

if __name__ == '__main__':
    curses.wrapper(main)
