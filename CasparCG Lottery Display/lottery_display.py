import sqlite3
import threading
import time
import configparser
import socket
import json

config = configparser.ConfigParser()
config.read('config.ini')

update_interval = int(config['General']['update_interval'])
db_path = config['Database']['path']

lottery_count = int(config['Lotteries']['lottery_count'])

lotteries = []
for i in range(1, lottery_count + 1):
    section = f'Lottery{i}'
    name = config[section]['name']
    background_color = config[section].get('background_color', '#2e2e2e')
    text_color = config[section].get('text_color', '#ffffff')
    table = config[section]['table']
    animated_background = config[section].getboolean('animated_background', False)
    lotteries.append({
        'id': i,
        'name': name,
        'background_color': background_color,
        'text_color': text_color,
        'animated_background': animated_background,
        'table': table
    })

class CasparCG:
    def __init__(self, host='localhost', port=5250):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.socket = None
        self.connect()

    def connect(self):
        self.socket = socket.create_connection((self.host, self.port))

    def send(self, command):
        with self.lock:
            self.socket.sendall((command + '\r\n').encode('utf-8'))
            response = self.socket.recv(4096)
            print(f"CasparCG Response: {response.decode('utf-8')}")

def get_latest_numbers(lottery):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT numbers FROM {lottery['table']}
        ORDER BY timestamp DESC LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    if result:
        numbers = result[0].split(',')
        return numbers
    else:
        return None

def send_to_casparcg(lottery, numbers, caspar):
    data = {
        'id': lottery['id'],
        'name': lottery['name'],
        'numbers': ' - '.join(numbers),
        'backgroundColor': lottery['background_color'],
        'textColor': lottery['text_color'],
        'animatedBackground': str(lottery['animated_background']).lower()
    }
    # Convertir los datos a una cadena JSON con ensure_ascii=False
    template_data = json.dumps(data, ensure_ascii=False)
    # Escapar las comillas dobles
    template_data_escaped = template_data.replace('"', '\\"')

    # Enviar el comando a CasparCG
    command = f'CG 1-1 UPDATE 1 "{template_data_escaped}"'
    print(f"Comando enviado a CasparCG: {command}")
    caspar.send(command)

def monitor_lottery(lottery, caspar):
    latest_numbers = None
    while True:
        numbers = get_latest_numbers(lottery)
        if numbers and numbers != latest_numbers:
            latest_numbers = numbers
            print(f"Nuevos números para {lottery['name']}: {numbers}")
            send_to_casparcg(lottery, numbers, caspar)
        time.sleep(update_interval)

def main():
    caspar = CasparCG('localhost', 5250)

    # Cargar la plantilla inicialmente
    caspar.send(f'CG 1-1 ADD 1 "lottery/lottery_template" 1')

    threads = []

    for lottery in lotteries:
        t = threading.Thread(target=monitor_lottery, args=(lottery, caspar))
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Saliendo...")

if __name__ == "__main__":
    main()
