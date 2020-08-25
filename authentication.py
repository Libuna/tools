#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import os
import json
import time
import getpass
import urllib3
import binascii
import requests
from cryptography.fernet import Fernet
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- vmanage authentication and create session --- #
def login():
	if not gs_userfile:
		os.system("clear")
		print('\n')
		print(' Configuration file is missing. Please run ~/viptela/setup.py')
		print('\n')
		exit()
	d_conf = {}
	s_key = ''
	f_conf = open(gs_conffile, 'r')
	f_conf_read = f_conf.read()
	if 'vmanage_ip' in f_conf_read:
		d_conf = json.loads(f_conf_read)
		f_conf.close()
	else:
		print('\n')
		print('  DECRYPTION KEY: ')
		s_key = getpass.getpass('').encode()
		print('\n')
		e_conf = f_conf_read.encode()
		f_conf.close()
		try:
			decryption = Fernet(s_key)
			j_conf = decryption.decrypt(e_conf).decode()
			d_conf = json.loads(j_conf)
		except binascii.Error as err:
			os.system("clear")
			print('\n')
			print('  DECRYPTION key is invalid. ')
			print('\n')
			exit()
		except ValueError:
			os.system("clear")
			print('\n')
			print('  DECRYPTION key is invalid. ')
			print('\n')
			exit()
	os.system("clear")

	try:
		print('\n')
		print("  Login started.\n")
		url = 'https://' + d_conf['vmanage_ip'] + '/j_security_check'
		login = {'j_username': d_conf['vmanage_username'] , 'j_password': d_conf['vmanage_password']}
		s_session = requests.session()
		login_response = s_session.post(url=url, data=login, verify=False)
		if b'<html>' in login_response.content:
			time.sleep(1)

		while b'<html>' in login_response.content:
			os.system("clear")
			print('\n')
			print("  Login failed.\n")
			s_vmanage_password = getpass.getpass('  Password: ')
			print('\n')
			url = 'https://' + d_conf['vmanage_ip'] + '/j_security_check'
			login = {'j_username': d_conf['vmanage_username'], 'j_password': s_vmanage_password}
			s_session = requests.session()
			login_response = s_session.post(url=url, data=login, verify=False)

			d_conf.update({'vmanage_password': s_vmanage_password})
			if not s_key:
				f_conf = open(gs_conffile, 'w')
				json.dump(d_conf, f_conf)
				f_conf.close()
			else:
				f_conf = open(gs_conffile, 'w')
				encryption = Fernet(s_key)
				j_conf = json.dumps(d_conf).encode()
				e_conf = encryption.encrypt(j_conf)
				s_conf = e_conf.decode()
				f_conf.write(s_conf)
				f_conf.close()

		print("  Login completed.\n")
		time.sleep(1)
		os.system("clear")
		return s_session, d_conf

	except NewConnectionError:
		print(' ')
		print('  !! vManage is not accessible !!\n')
		exit()
	except MaxRetryError:
		print(' ')
		print('  !! vManage is not accessible !!\n')
		exit()
	except ConnectionError:
		print(' ')
		print('  !! vManage is not accessible !!\n')
		exit()
	except TimeoutError:
		print(' ')
		print('  !! vManage is not accessible !!\n')
		exit()

# --- main --- #
os.system("clear")
gs_userpath = os.path.expanduser('~')
gs_userfile = os.path.isfile(gs_userpath + '/viptela/.conf')
gs_conffile = gs_userpath + '/viptela/.conf'

