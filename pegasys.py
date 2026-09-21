#!/usr/bin/env python3

import sqlite3
import socket
import sys, os

class Pegasys:

	def __init__(self):
		self.initDb()

		# setup UDP listener based on HardSys entries
		hwsys = {}
		self.cur.execute('SELECT HSID, NAME, TCPIPOUT FROM HardSys WHERE DRIVERTYPE = "I"')
		for row in self.cur.fetchall():
			print(f'Setting up socket for Hardware System "{row[1]}" (HSID {row[0]}) @ {row[2]}')
			hwsys[row[2]] = str(row[0])

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.bind(('', 23))
		while True:
			message, address = server_socket.recvfrom(1024)
			message = message.decode('utf-8')
			if address[0] in hwsys:
				hwsysId = hwsys[address[0]]
				print(hwsysId+'>', message)
				if message.startswith('%') and message.endswith('#'):
					response = self.handleMessage(hwsysId, message[1:-1])
					if response:
						print(hwsysId+'<', response)
						server_socket.sendto(response.encode('utf-8'), address)
			else:
				print('?!', f'ignoring unknown IP: {address[0]}')

	def handleMessage(self, hsid, message):
		try:
			if message.startswith('39V'):
				point = message[3:7].split(':')
				if len(point) != 2:
					raise Exception('unexpected 39V message: invalid point')

				payload = message[7:].split(',')
				if len(payload) != 7:
					raise Exception('unexpected 39V message: invalid payload')

				cardno = payload[3]
				if self.checkAccess(cardno, hsid, point[0], point[1]):
					print('  ', f'access request for {cardno} @ {hsid} @ {point[0]}:{point[1]} --> OK')
					return '&F#'
				else:
					print('  ', f'access request for {cardno} @ {hsid} @ {point[0]}:{point[1]} --> DENY')
					return '!F#'

			else:
				raise Exception('unknown opcode')
		except Exception as e:
			print(hsid+'!', e)
			return None

	def initDb(self):
		self.con = sqlite3.connect('data.db')
		self.cur = self.con.cursor()

	def checkAccess(self, cardno, hsid, controller, reader):
		queryPoint = 'SELECT ID FROM Points WHERE HSID=:HSID AND SYS_ADDR=:SYS_ADDR'
		# crazy: Level "ID" is stored decremented by 1 in "User" table column "LEVEL"
		queryLevel = 'SELECT (LEVEL - 1) FROM LevelRel WHERE HSID=:HSID AND POINT IN ('+queryPoint+')'

		self.cur.execute(
			'SELECT CARDNO, NAME, FIRSTNAME FROM User WHERE '
			+'CAST(CARDNO as INT) = :CARDNO '
			+'AND ('
				+'LEVEL IN ('+queryLevel+') '
				+'OR PERS_AP1 IN ('+queryPoint+') '
				+'OR PERS_AP2 IN ('+queryPoint+') '
				+'OR PERS_AP3 IN ('+queryPoint+') '
				+'OR PERS_AP4 IN ('+queryPoint+') '
			+')',
			{'CARDNO':int(cardno), 'HSID':int(hsid), 'SYS_ADDR':controller+':'+reader}
		)
		for row in self.cur.fetchall():
			#print(row)
			return True
		return False

if __name__ == '__main__':
	p = Pegasys()
