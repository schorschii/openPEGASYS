#!/usr/bin/env python3

import sqlite3
import sys, os

DATA_DB  = 'data.db'
QUEUE_DB = 'queue.db'

class PegaCLI:

	def __init__(self):
		self.initDb()

	def initDb(self):
		self.ccon = sqlite3.connect(QUEUE_DB)
		self.ccur = self.ccon.cursor()

	def setAccess(self, cardno, level, ap1, ap2, ap3, ap4):
		self.ccur.execute(
			'INSERT INTO UserChange(CARDNO, LEVEL, PERS_AP1, PERS_AP2, PERS_AP3, PERS_AP4) '
			+'VALUES (:CARDNO, :LEVEL, :PERS_AP1, :PERS_AP2, :PERS_AP3, :PERS_AP4)'
			# crazy: Level "ID" is stored decremented by 1 in "User" table column "LEVEL"
			,{'CARDNO':int(cardno), 'LEVEL':int(level), 'PERS_AP1':ap1, 'PERS_AP2':ap2, 'PERS_AP3':ap3, 'PERS_AP4':ap4}
		)
		self.ccon.commit()
		print('SQlite rows affected:', self.ccur.rowcount)

if __name__ == '__main__':
	pcli = PegaCLI()
	if len(sys.argv) > 1:
		if sys.argv[1] == 'user' and len(sys.argv) == 8:
			pcli.setAccess(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
		else:
			print('Unrecognized command')
