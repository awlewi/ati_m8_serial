#!/usr/bin/python3
#
#   ati_m8_serial.py

#   establishes serial connection to ATI Axia M8 sensor for testing functionality
#

from ati_m8_serial import atiM8serial as ati 


force = ati(3)
#force.open(3)
for i in range (1000):
	print(force.readForce())