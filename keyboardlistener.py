import keyboard


def print_pressed_keys(e):
    line = ', '.join(str(code) for code in keyboard._pressed_events)
    # print(line)
    if line == '56, 42, 29' or line == '56, 29, 42' or line == '29, 56, 42' \
            or line == '29, 42, 56' or line == '42, 29, 56' or line == '42, 56, 29':  # ctrl+shift+alt组合键表示启动识别程序
        f = open('keylogger.txt', 'w')
        f.write('True')
        f.close()
    if line == '44, 29, 56' or line == '44, 56, 29' or line == '29, 44, 56' or \
            line == '29, 56, 44' or line == '56, 29, 44' or line == '56, 44, 29':  # ctrl+alt+z组合键表示关闭识别程序
        f = open('keylogger.txt', 'w')
        f.write('False')
        f.close()
    if line == '44, 42' or line == '42, 44':
        f = open('endflag.txt', 'w')
        f.write('True')
        f.close()


keyboard.hook(print_pressed_keys)
keyboard.wait()