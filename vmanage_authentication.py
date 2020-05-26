#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  informe@email.cz             #

import os
import re
import json
import time
import requests
import getpass
import urllib3
from urllib3.exceptions import NewConnectionError
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login():

	# --- system settings --- ##
	s_vmanage_ip = '166.60.191.211'
	s_vedge_os_version = '18.4.4'

	# --- vmanage authentication and create session --- #
	print("\n")
	print("  >> vManage authentication: started   <<\n")
	j_uinfo = {}
	s_userpath = os.path.expanduser('~')
	s_userfile = os.path.isfile(s_userpath + '/.uinfo')
	if s_userfile:
		f_uinfo = open(s_userpath + '/.uinfo', 'r')
		j_uinfo = json.load(f_uinfo)
		f_uinfo.close()
		s_vmanage_username = j_uinfo['user']
		s_vmanage_password = j_uinfo['passwd']
		s_email = j_uinfo['email']

	else:
		s_vmanage_username = input('   - Username: ')
		s_vmanage_password = getpass.getpass('   - Password: ')
		s_email = input('   - Email address: ')
		s_email = s_email.strip()
		s_email_re = re.search('@.*\..*', s_email)
		while s_email_re is None:
			print("   ! Email has incorrect format !\n")
			s_email = input('   - Email address: ')
			s_email = s_email.strip()
			s_email_re = re.search('@.*\..*', s_email)

		j_uinfo.update({'user':s_vmanage_username})
		j_uinfo.update({'passwd':s_vmanage_password})
		j_uinfo.update({'email':s_email})
		f_uinfo = open(s_userpath + '/.uinfo', 'w')
		json.dump(j_uinfo, f_uinfo)
		f_uinfo.close()
		os.chmod(s_userpath + '/.uinfo',0o600)

	try:
		url = 'https://' + s_vmanage_ip + '/j_security_check'
		login = {'j_username': s_vmanage_username , 'j_password': s_vmanage_password}
		s_session = requests.session()
		login_response = s_session.post(url=url, data=login, verify=False)
		if b'<html>' in login_response.content:
			print('')
			print("  !! vManage authentication: failed !!")
			time.sleep(1)

		while b'<html>' in login_response.content:
			os.system("clear")
			print("\n")
			print("  >> vManage authentication: started   <<\n")
			s_vmanage_username = input('   - Username: ')
			s_vmanage_password = getpass.getpass('   - Password: ')
			url = 'https://' + s_vmanage_ip + '/j_security_check'
			login = {'j_username': s_vmanage_username, 'j_password': s_vmanage_password}
			s_session = requests.session()
			login_response = s_session.post(url=url, data=login, verify=False)

			j_uinfo.update({'user': s_vmanage_username})
			j_uinfo.update({'passwd': s_vmanage_password})
			f_uinfo = open(s_userpath + '/.uinfo', 'w')
			json.dump(j_uinfo, f_uinfo)
			f_uinfo.close()
			os.chmod(s_userpath + '/.uinfo', 0o600)

		print("     ...")
		print("  >> vManage authentication: completed <<")
		time.sleep(1)
		return s_vmanage_ip, s_vmanage_username, s_vmanage_password, s_session, s_email, s_vedge_os_version, j_uinfo

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
