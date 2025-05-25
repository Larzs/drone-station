import sqlite3
import requests
import json
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

timeout = 1
endpoint = os.getenv('ENDPOINT')
path = os.getenv('PROJECT_PATH')

try:
	requests.head(endpoint, timeout=timeout)

	connection = sqlite3.connect(path + "/drones.db")
	cursor = connection.cursor()

	with open('/home/gs/sniffer/last_update') as f:
		date = f.read()

	res = cursor.execute("SELECT * FROM drones where stamp > ?", (date,))
	rows = cursor.fetchall()
	connection.close()

	headers = {'content-type': 'application/json'}
	url = endpoint + '/send/'

	timeToRegister = datetime.datetime.now()

	status = requests.post(url, data=json.dumps(rows), headers=headers)

	if status.status_code == 200:
		with open(path + "/last_update", 'w') as file:
		    file.write(f'{timeToRegister:%Y-%m-%d %H:%M:%S%z}')

except requests.ConnectionError:
	print("The internet connection is down")



