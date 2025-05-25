from scapy.all import *
from threading import Thread, Event
from time import sleep
import datetime
import sqlite3
import RPi.GPIO as GPIO

from parser_handler import DefaultHandler, DjiHandler, AsdStanHandler
from parsers import Parser

handler=AsdStanHandler(DjiHandler(DefaultHandler(None)))

triggerPIN = 14

class Sniffer(Thread):
	def  __init__(self, interface="monitors"):
		super().__init__()
		self.daemon = True
		self.socket = None
		self.interface = interface
		self.stop_sniffer = Event()

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(triggerPIN, GPIO.OUT)
		self.buzzer = GPIO.PWM(triggerPIN, 1000)

		self.connection = sqlite3.connect("/home/gs/sniffer/drones.db", check_same_thread=False)
		cursor = self.connection.cursor()
		cursor.execute("""CREATE TABLE IF NOT EXISTS drones(serial_number TEXT, oui TEXT, stamp TEXT, lang REAL, lat REAL)""")
		self.connection.commit()

	def run(self):
		self.socket = conf.L2listen(
			iface=self.interface,
			filter="type mgt subtype beacon"
		)

		sniff(
			opened_socket=self.socket,
			prn=self.process_packet,
			stop_filter=self.should_stop_sniffer
		)

	def join(self, timeout=None):
		self.stop_sniffer.set()
		super().join(timeout)

	def should_stop_sniffer(self, packet):
		return self.stop_sniffer.is_set()

	def process_packet(self, packet):
		if packet.haslayer(Dot11EltVendorSpecific) and packet.haslayer(Dot11Beacon):
			vendor_data: Dot11EltVendorSpecific = packet.getlayer(Dot11EltVendorSpecific)
			while vendor_data:
				layer_oui = Parser.dec2hex(vendor_data.oui)

				if handler.is_drone(layer_oui):
					remote_id = handler.parse(vendor_data.info, layer_oui)
					if remote_id:
						self.buzzer.start(10)
						sleep(0.05)
						self.buzzer.stop()

						cursor = self.connection.cursor()
						cursor.execute(""" INSERT INTO drones(serial_number, oui, stamp, lang, lat) VALUES (?, ?, ?, ?, ?)""", [remote_id.serial_number, remote_id.oui, datetime.datetime.now(), remote_id.lat, remote_id.lng])

						self.connection.commit()

						return print(datetime.datetime.now(), remote_id.lat, remote_id.lng)
				else:
					vendor_data: Dot11EltVendorSpecific = vendor_data.payload.getlayer(Dot11EltVendorSpecific)
					continue

sniffer = Sniffer()

print('Starting sniffer')
sniffer.start()

try:
	while True:
		sleep(100)
except KeyboardInterrupt:
	print("[*] Stop sniffing")
	GPIO.cleanup()
	sniffer.join(2.0)

	if sniffer.is_alive():
		sniffer.socket.close()
