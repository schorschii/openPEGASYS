#!/usr/bin/env python3

import sqlite3
import socket
import sys, os
import inotify.adapters
import threading

DATA_DB  = 'data.db'
QUEUE_DB = 'queue.db'

class QueueListener(threading.Thread):

	def __init__(self, pegad, *args, **kwargs):
		self.pegad = pegad
		super(QueueListener, self).__init__(*args, **kwargs)
		self.daemon = True

	def initDb(self):
		self.i = inotify.adapters.Inotify()
		self.i.add_watch(QUEUE_DB)

		self.ccon = sqlite3.connect(QUEUE_DB)
		self.ccur = self.ccon.cursor()
		self.ccur.execute('CREATE TABLE IF NOT EXISTS UserChange(ID INTEGER PRIMARY KEY AUTOINCREMENT, CARDNO, LEVEL, PERS_AP1, PERS_AP2, PERS_AP3, PERS_AP4)')
		self.workingOnQueue = False
		self.queueChanged() # process items added when pegad was not running

	def run(self, *args, **kwargs):
		self.initDb()
		for event in self.i.event_gen(yield_nones=False):
			(_, type_names, path, filename) = event
			if 'IN_MODIFY' not in type_names: continue
			if not self.workingOnQueue:
				print('FS',f'PATH={path} FILENAME={filename} EVENT_TYPES={type_names}')
				self.queueChanged()

	def queueChanged(self):
		self.workingOnQueue = True
		self.ccur.execute('SELECT ID, CARDNO, LEVEL, PERS_AP1, PERS_AP2, PERS_AP3, PERS_AP4 FROM UserChange')
		for row in self.ccur.fetchall():
			try:
				self.pegad.setAccess(row[1], row[2], row[3], row[4], row[5], row[6])
				self.ccur.execute('DELETE FROM UserChange WHERE ID = :ID', {'ID':row[0]})
			except Exception as e:
				print(e)
		self.ccon.commit()
		self.workingOnQueue = False

class PegaD:

	def __init__(self):
		self.initDb()

	def initDb(self):
		self.con = sqlite3.connect(DATA_DB, check_same_thread=False)
		self.cur = self.con.cursor()

		self.fileListener = QueueListener(self)
		self.fileListener.start()

	def getHardwareSystems(self, verbose=False):
		hwsys = {}
		self.cur.execute('SELECT HSID, NAME, TCPIPOUT FROM HardSys WHERE DRIVERTYPE = "I"')
		for row in self.cur.fetchall():
			if(verbose): print(f'Init HSID {row[0]} "{row[1]}" @ {row[2]}')
			hwsys[row[2]] = str(row[0])
		return hwsys

	def listen(self):
		# setup UDP listener based on HardSys entries
		hwsys = self.getHardwareSystems(True)
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.server_socket.bind(('', 23))
		while True:
			message, address = self.server_socket.recvfrom(1024)
			message = message.decode('utf-8')
			if address[0] in hwsys:
				hwsysId = hwsys[address[0]]
				print(hwsysId+'>', message)
				response = self.handleMessage(hwsysId, message)
				if response: self.send(response)
			else:
				print('?!', f'ignoring unknown IP: {address[0]}')

	def send(self, receiver, payload):
		for ip, hsid in self.getHardwareSystems().items():
			if ip != receiver: continue
			print(hsid+'<', payload)
			self.server_socket.sendto(payload.encode('utf-8'), (ip, 10001))

	def handleMessage(self, hsid, message):
		try:
			if not message.startswith('%') or not message.endswith('#'):
				raise Exception('message corrupt, expecting % <-> #')

			checksum = self.checksum(message[0:-3])
			advertisedChecksum = message[-3:-1].upper()
			if advertisedChecksum != checksum:
				raise Exception('message checksum error, '+advertisedChecksum+' != '+checksum)

			advertisedLength = int(message[1:3])
			if len(message) != advertisedLength:
				raise Exception('unexpected message length, '+str(len(message))+' != '+str(advertisedLength))

			opcode = message[3]
			if opcode == 'V':
				point = message[4:8].split(':')
				if len(point) != 2:
					raise Exception('unexpected V message: invalid point')

				payload = message[8:].split(',')
				if len(payload) != 7:
					raise Exception('unexpected V message: invalid payload')

				cardno = payload[3]
				print('  ', f'access info for {cardno} @ {hsid} @ {point[0]}:{point[1]}')
				return '&F#'

			else:
				raise Exception('unknown opcode: '+opcode)

		except Exception as e:
			print(hsid+'!', e)
			return None

	def checksum(self, input):
		sum = 0
		for c in input:
			sum += ord(c)
		return hex(sum % 256)[2:].zfill(2).upper()

	def buildCmd(self, payload):
		tmpCmd = '%' + str(len(payload)+5) + payload + ' '
		tmpCmd += self.checksum(tmpCmd) + '#'
		return tmpCmd

	def getControllerModule(self, pointId):
		if not pointId: return None
		self.cur.execute(
			'SELECT HSID, SYS_ADDR FROM Points WHERE ID = :ID'
			,{'ID':int(pointId)}
		)
		for row in self.cur.fetchall():
			return row[0], row[1]

	def setAccess(self, cardno, level, ap1, ap2, ap3, ap4):
		for ip, hsid in self.getHardwareSystems().items():
			cmds = [
				self.buildCmd('C*:*U='+str(cardno)+',0,D'),
				self.buildCmd('C*:*U='+str(cardno)+',0,E,'+str(level)+',0,D,,0,0'),
			]
			c1 = self.getControllerModule(ap1)
			c2 = self.getControllerModule(ap2)
			c3 = self.getControllerModule(ap3)
			c4 = self.getControllerModule(ap4)
			if c1 and str(c1[0]) == str(hsid): cmds.append(self.buildCmd('C'+c1[1]+'U='+str(cardno)+',0,A,E'))
			if c2 and str(c2[0]) == str(hsid): cmds.append(self.buildCmd('C'+c2[1]+'U='+str(cardno)+',0,A,E'))
			if c3 and str(c3[0]) == str(hsid): cmds.append(self.buildCmd('C'+c3[1]+'U='+str(cardno)+',0,A,E'))
			if c4 and str(c4[0]) == str(hsid): cmds.append(self.buildCmd('C'+c4[1]+'U='+str(cardno)+',0,A,E'))
			for cmd in cmds: self.send(ip, cmd)

		self.cur.execute(
			'UPDATE User SET LEVEL = :LEVEL, PERS_AP1 = :PERS_AP1, PERS_AP2 = :PERS_AP2, PERS_AP3 = :PERS_AP3, PERS_AP4 = :PERS_AP4 '
			+'WHERE CAST(CARDNO as INT) = :CARDNO'
			# crazy: Level "ID" is stored decremented by 1 in "User" table column "LEVEL"
			,{'CARDNO':int(cardno), 'LEVEL':int(level)-1, 'PERS_AP1':ap1, 'PERS_AP2':ap2, 'PERS_AP3':ap3, 'PERS_AP4':ap4}
		)
		self.con.commit()
		print('SQ', 'rows affected:', self.cur.rowcount)

if __name__ == '__main__':
	pd = PegaD()
	pd.listen()
