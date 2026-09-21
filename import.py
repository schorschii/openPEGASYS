#!/usr/bin/env python3

from dbfread import DBF
import sqlite3
import sys, os

USER_COLUMNS = ['CARDNO', 'SITEREF', 'ISSUESTATE', 'LEVEL', 'PIN_NO', 'CARDUSE', 'VALID_FROM', 'VALID_TO', 'HOL_FROM', 'HOL_TO', 'LOCATION', 'LASTRECORD', 'LASTTIME', 'LASTDATE', 'NAME', 'FIRSTNAME', 'ADDRESS1', 'ADDRESS2', 'ADDRESS3', 'ADDRESS4', 'ADDRESS5', 'ADDRESS6', 'ADDRESS7', 'TELNO', 'CARNO', 'DEPT', 'JOBTITLE', 'TELEXT', 'IMGNAME', 'CARDIDNO', 'BADGEDSN', 'ISSUEDATE', 'PRINTREQ', 'PRINTDATE', 'PERS_AP1', 'PERS_AP2', 'PERS_AP3', 'PERS_AP4', 'TIMEPLAN', 'USERTYPE', 'VNAME', 'VFIRSTNAME', 'VISITORTYP', 'EXTRA1', 'EXTRA2', 'EXTRA3', 'EXTRA4', 'NOTES', 'SIGNIN', 'SIGNOUT', 'AUTOSGNIN', 'AUTOSGNOUT', 'TIME_FROM', 'TIME_TO', 'KEEPCARD', 'AC_CNTRL', 'CARDGROUP', 'PERM_ENABL', 'EXPORTED', 'IMPORTED', 'SIGNATURE']
POINTS_COLUMNS = ['NAME', 'SYS_ADDR', 'HSID', 'TYPE', 'SWIPE', 'D_RELAY_TM', 'D_RELAY_TP', 'D_CONTROL', 'UL_T_FRM', 'TRANMODE', 'EGRESS', 'D_MONITOR', 'FORCED_ALM', 'OPEN_ALM', 'D_OP_A_DEL', 'FORCED_WRN', 'OPEN_WRN', 'D_OP_W_DEL', 'GLOBAL', 'ENTERING', 'EXITING', 'TIMERECORD', 'SHUNT', 'A_PASS_LOC', 'PIN_PAD', 'PIN_PAD_TP', 'PIN_PAD_TM', 'AUX_INP', 'AUX_TAMPER', 'AUX_T_FRM', 'AUX_OP', 'AUX_TICK_1', 'AUX_TICK_2', 'AUX_OP_FRM', 'AUX_PIN', 'INPUTDESC', 'OUTPUTDESC', 'INPACT1', 'INPACT2', 'INPACT3', 'INPACT4', 'INPFILE', 'INPTAMP1', 'INPTAMP2', 'INPTAMP3', 'INPTAMP4', 'INPTMPFILE', 'FORCEDACT1', 'FORCEDACT2', 'FORCEDACT3', 'FORCEDACT4', 'FORCEDFILE', 'OPENACT1', 'OPENACT2', 'OPENACT3', 'OPENACT4', 'OPENFILE', 'SELECTED', 'FORCEDPTY', 'OPENPTY', 'INPPTY', 'INPTAMPPTY', 'PTY_ENABLE', 'DOOR_TMPR', 'EGR_TMPR', 'CLIC_ENABL', 'MONTPRPTY', 'EGRTPRPTY', 'MONTPRACT1', 'MONTPRACT2', 'MONTPRACT3', 'MONTPRACT4', 'MONTPRFILE', 'EGRTPRACT1', 'EGRTPRACT2', 'EGRTPRACT3', 'EGRTPRACT4', 'EGRTPRFILE', 'ID', 'RDRTYPE', 'CRD', 'TRMTZ', 'TRMOVRD', 'PINTZ', 'ATIME', 'STIME', 'APT', 'D601', 'D602', 'D603', 'D604', 'D605', 'D606', 'D607', 'D608', 'D609', 'D610', 'D611', 'D612']
FRAMES_COLUMNS = ['NAME', 'E1', 'HSTART1', 'MSTART1', 'HEND1', 'MEND1', 'ZONE1', 'E2', 'HSTART2', 'MSTART2', 'HEND2', 'MEND2', 'ZONE2', 'E3', 'HSTART3', 'MSTART3', 'HEND3', 'MEND3', 'ZONE3', 'E4', 'HSTART4', 'MSTART4', 'HEND4', 'MEND4', 'ZONE4', 'E5', 'HSTART5', 'MSTART5', 'HEND5', 'MEND5', 'ZONE5', 'E6', 'HSTART6', 'MSTART6', 'HEND6', 'MEND6', 'ZONE6', 'E7', 'HSTART7', 'MSTART7', 'HEND7', 'MEND7', 'ZONE7', 'E8', 'HSTART8', 'MSTART8', 'HEND8', 'MEND8', 'ZONE8', 'E9', 'HSTART9', 'MSTART9', 'HEND9', 'MEND9', 'ZONE9', 'E10', 'HSTART10', 'MSTART10', 'HEND10', 'MEND10', 'ZONE10', 'ID']
LEVEL_COLUMNS = ['NAME', 'FILE_NUM', 'APOVRD', 'VISITORAL', 'ID']
LEVEL_REL_COLUMNS = ['LEVEL', 'POINT', 'FRAME', 'HSID', 'ID']
HARD_SYS_COLUMNS = ['HSID', 'NAME', 'DRIVERTYPE', 'PASSWORD', 'COMPORT', 'TAPINAME', 'COMPNAME', 'TELNOOUT', 'THISTELNO', 'SECMODEM', 'TCPIPOUT', 'TCPIPPORTO', 'TCPIPIN', 'TCPIPPORTI', 'DISCONTIME', 'CONTACTTIM', 'CONTPERIOD', 'DATATOSEND', 'SENDHIST', 'REMTIMEOUT', 'TIMEOFFSET', 'PLUSMINUS', 'SEND75FULL', 'LASTCONTAC', 'RESET', 'INIT', 'ESC', 'HANGUP', 'DIALTYPE', 'SITECONTAC', 'CONFTIMEN', 'CONFPRDEN', 'TIMEDCONT', 'DIALINTIME', 'DIALINDAY', 'PCMASTER', 'RCCLOCK', 'HWADDRESS', 'HWSYNCH', 'DOUPDATE', 'DISCTIME', 'ONLINE', 'ALARMPTY', 'PTY_ENABLE', 'ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTIONFILE', 'IMMEDIATE']

def main():
	con, cur = initDb()

	if len(sys.argv) > 1:
		for i in range(1, len(sys.argv)):
			importDbase(sys.argv[i], cur)
	else:
		print('Note: no file to import')

	con.commit()

def initDb():
	# open/create db
	con = sqlite3.connect('data.db')
	cur = con.cursor()
	# create schema
	cur.execute('CREATE TABLE IF NOT EXISTS User(' + ','.join(USER_COLUMNS) + ', PRIMARY KEY(CARDIDNO))')
	cur.execute('CREATE TABLE IF NOT EXISTS Points(' + ','.join(POINTS_COLUMNS) + ', PRIMARY KEY(ID))')
	cur.execute('CREATE TABLE IF NOT EXISTS Frames(' + ','.join(FRAMES_COLUMNS) + ', PRIMARY KEY(ID))')
	cur.execute('CREATE TABLE IF NOT EXISTS Levels(' + ','.join(LEVEL_COLUMNS) + ', PRIMARY KEY(ID))')
	cur.execute('CREATE TABLE IF NOT EXISTS LevelRel(' + ','.join(LEVEL_REL_COLUMNS) + ', PRIMARY KEY(LEVEL,POINT,FRAME,HSID))')
	cur.execute('CREATE TABLE IF NOT EXISTS HardSys(' + ','.join(HARD_SYS_COLUMNS) + ', PRIMARY KEY(HSID))')
	return con, cur

def importDbase(filename, cur):
	if os.path.basename(filename).upper() == 'USER32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO User(' + ','.join(USER_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	elif os.path.basename(filename).upper() == 'LEVELS32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO Levels(' + ','.join(LEVEL_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	elif os.path.basename(filename).upper() == 'POINTS32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO Points(' + ','.join(POINTS_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	elif os.path.basename(filename).upper() == 'FRAMES32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO Frames(' + ','.join(FRAMES_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	elif os.path.basename(filename).upper() == 'LEVELREL32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO LevelRel(' + ','.join(LEVEL_REL_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	elif os.path.basename(filename).upper() == 'HARDSYS32.DBF':
		for record in DBF(filename):
			cur.execute(
				'INSERT INTO HardSys(' + ','.join(HARD_SYS_COLUMNS) + ') VALUES (:' + ',:'.join(record.keys()) + ')',
				record
			)
	else:
		print('Unknown database file:', os.path.basename(filename))

if __name__ == '__main__':
	main()
