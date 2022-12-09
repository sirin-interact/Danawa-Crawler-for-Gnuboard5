import random
import time
import subprocess
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request
import configparser
import sys, os, traceback, types
import psutil
import hashlib

from danawa_crawler import config
from danawa_crawler.config import LOGLEVEL

def print_log(level, msg):
	if level >= config.CFG_LOGLEVEL:
		nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		print(nowtime + " : " + msg)

def rand_mac():
	return "74%02x%02x%02x%02x%02x" % (
		random.randint(0, 255),
		random.randint(0, 255),
		random.randint(0, 255),
		random.randint(0, 255),
		random.randint(0, 255)
		)

def disable_network():
	args = 'netsh interface set interface name="로컬 영역 연결" admin="disabled"'
	subprocess.call(args)

def enable_network():
	args = 'netsh interface set interface name="로컬 영역 연결" admin="enabled"'
	subprocess.call(args)

def change_random_macaddress():
	mac = rand_mac()

	regPath = 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4D36E972-E325-11CE-BFC1-08002BE10318}\\' + '1' # 마지막 숫자는 랜카드 인덱스, PC마다 다름.

	args = ['reg', 'add', regPath, '/f', '/v', 'NetworkAddress', '/d', mac]
	subprocess.call(args)

	time.sleep(1)

	disable_network()

	time.sleep(2)

	enable_network()

def killProcess(processName):
	args = 'taskkill /im ' + processName + ' /f'
	subprocess.call(args)

def execFileExternal(sCmd):
	subprocess.call(sCmd)

def execFileExternal2(sCmd, arg):
	cmd = ['powershell.exe', 'Start-Process', sCmd, arg,'-Verb','runAs']
	subprocess.run(cmd ,shell=True)

def execFileExternal3(args):
	subprocess.call(args)


def downloadFile(url, saveFilePath):
	try:
		if os.path.exists(saveFilePath):
			os.remove(saveFilePath)

		with urllib.request.urlopen(url) as response, open(saveFilePath, 'wb') as out_file:
			data = response.read() # a `bytes` object
			out_file.write(data)
	except:
		traceback.print_exc()

def get_window_uuid():
	current_machine_id = str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()
	return current_machine_id

def writeConfig(vname, val):
	config = configparser.ConfigParser()

	curDir = os.getcwd()
	config.read(curDir + '/config.ini')

	config['DEFAULT'][vname] = str(val)

	with open(curDir + '/config.ini', 'w') as configfile:
		config.write(configfile)

def readConfigString(vname, defaultVal=''):
	config = configparser.ConfigParser()

	curDir = os.getcwd()
	config.read(curDir + '/config.ini')

	if not vname in config['DEFAULT']:
		return defaultVal

	return config['DEFAULT'][vname];

def readConfigInt(vname, defaultVal=0):
	config = configparser.ConfigParser()

	curDir = os.getcwd()
	config.read(curDir + '/config.ini')

	if not vname in config['DEFAULT']:
		return defaultVal

	return int(config['DEFAULT'][vname]);

def isProcessRunning(processName):
	for proc in psutil.process_iter():
		try:
			if processName.lower() in proc.name().lower():
				return True
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass

	return False;

def get_md5(str):
	return hashlib.md5(str.encode()).hexdigest()

def inputTextElement(el, text):
	for i in range(0, len(text)):
		el.send_keys(text[i])
		time.sleep(0.3)

def inputTextElementWithEnter(el, text):
	for i in range(0, len(text)):
		el.send_keys(text[i])
		time.sleep(0.3)

	el.send_keys(Keys.RETURN)

def clickRandomElement(driver, elList):
	isClicked = False

	try:
		if len(elList) > 0 :
			actions = ActionChains(driver)

			randIdx = random.randint(0, len(elList) - 1)
			el = elList[randIdx]
			actions.move_to_element(el).perform()
			el.click()

			isClicked = True

	except Exception:
		isClicked = False
		traceback.print_exc()

	return isClicked

def clickElement(driver, el):
	el.click()

def clickElementMulti(driver, el, count):
	for i in range (0, count):
		el.click()
		time.sleep(0.1)

def moveElement(driver, el):
	actions = ActionChains(driver)

	actions.move_to_element(el).perform()

def keyDown(driver, keyCode):
	actions = ActionChains(driver)
	actions.key_down(keyCode).key_up(keyCode).perform()


def sendKeycodeMultiply(el, keyCode, multi):
	for i in range(0, multi):
		el.send_keys(keyCode)
		time.sleep(0.2)