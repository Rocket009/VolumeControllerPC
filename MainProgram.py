from AudioController import AudioController
import serial
from time import sleep
from SpotifyControls import SpotifyControls
import threading
import json
import ctypes
from os import _exit

DefaultConfig = {'app1':" ",'app2':" ",'username': " ",'clientid': " ",'clientsecret': " ",'playlistid': " "}
serialPort = None
def GetCurrentTrack():
	old_track = ""
	while(True):
		track = sp.CurrentTrack()
		if track != old_track:													
			#print(track)
			if serialPort != None and serialPort.writable():
				try:
					serialPort.write(bytes(track + '\n','Ascii'))
				except:
					pass
			old_track = track
		sleep(2)
def GetConfig() -> dict:
	f = None
	try:
		f = open("config.txt","r")
	except FileNotFoundError:
		try:
			f = open("config.txt","w")
			f.write(json.dumps(DefaultConfig))
			f.close()
		except FileExistsError:
			ctypes.windll.user32.MessageBoxW(0,u"Error, please delete config file and restart.",u"Error",0)
	if not f.closed:
		text = json.loads(f.read())
		f.close()
		return text
	else:
		return DefaultConfig

def CheckConfig(conf: dict) -> bool:
	if conf['app1'] == " ":
		return False
	elif conf['app2'] == " ":
		return False
	elif conf['username'] == " ":
		return False
	elif conf['clientid'] == " ":
		return False
	elif conf['clientsecret'] == " ":
		return False
	elif conf['playlistid'] == " ":
		return False
	else:
		return True
def Polling():
	while True:
		if serialPort != None and serialPort.writable():
			try:
				serialPort.write(bytes('P' + '\n','Ascii'))
				sleep(4)
			except:
				sleep(4)
if __name__ == '__main__':
	available = []
	conf = GetConfig()
	if not CheckConfig(conf):
		ctypes.windll.user32.MessageBoxW(0,u"Config file is not set. Please edit config file and restart.",u"Error",0)
		_exit(1)
	while True:
		try:
			for i in range(256):
				try:
					s = serial.Serial('COM' + str(i))
					available.append(s.portstr)
					s.close()
				except serial.SerialException:
					pass
			serialPort = serial.Serial(port=available[0], baudrate=9600, bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
			if serialPort.is_open:
				serialPort.close()
				break
		except:
			ctypes.windll.user32.MessageBoxW(0,u"Error could not find any devices.",u"Error",0)
	if serialPort != None:
			serialPort.open()
			cont1 = AudioController(conf['app1'])
			cont2 = AudioController(conf['app2'])
			sp = SpotifyControls(conf)
			thread = threading.Thread(target=GetCurrentTrack)
			thread2 = threading.Thread(target=Polling)
			thread.start()
			thread2.start()
			old_c = 0
			while(True):
				token = sp.auth_manager.get_cached_token()
				if sp.auth_manager.is_token_expired(token):
					sp.refresh_spotify()
				try:
					try:
						data = serialPort.read_until()
					except serial.SerialException:
						ctypes.windll.user32.MessageBoxW(0,u"Arduino Disconnected.",u"Error",0)
						_exit(1)
					value = data.decode('Ascii')
					if value[0] == 'A':
						ivalue = value[1:]
						v = float(ivalue)
						vf = v / 100
						cont2.set_volume(vf)
					elif value[0] == 'B':
						ivalue = value[1:]
						v = float(ivalue)
						vf = v / 100
						cont1.set_volume(vf)
					elif value[0] == 'S':
						sp.AddTrack(conf['playlistid'])
					elif value[0] == 'C':
						ivalue = value[1:]
						v = float(ivalue)
						vf = v / 100
						if old_c > vf or old_c < vf:
							AudioController.SetMasterVolume(vf)
							vf = old_c
					elif value[0] == 'N':
						track = sp.CurrentTrack()
						serialPort.write(bytes(track + '\n','Ascii'))
				except OSError:
					pass
	else:
		ctypes.windll.user32.MessageBoxW(0,u"No serial port.",u"Error",0)




		


		

