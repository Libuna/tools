#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import authentication
import os
import re
import json
import time
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- Cisco auth token request and serial verification --- #
def smart_account_verify_serial_number__verification(d_conf, s_vedge_sn):
	os.system("clear")
	url = 'https://cloudsso.cisco.com/as/token.oauth2'
	token = {'client_id': d_conf['cisco_client_id'], 'client_secret': d_conf['cisco_client_secret'],
	         'username': d_conf['cisco_username'],
	         'password': d_conf['cisco_password'], 'grant_type': 'password'}
	s_cisco_session = requests.session()
	s_cisco_login_response = s_cisco_session.post(url=url, data=token, verify=False)
	d_cisco_login_response = json.loads(s_cisco_login_response.content.decode('utf8'))
	c_cisco_login_error = 0
	if 'error' in d_cisco_login_response.keys():
		c_cisco_login_error += 1
		print("\n")
		print('  !! Cisco authentication failed. Please run ./setup.py to update Cisco credentials.\n')
		time.sleep(2)

	s_cisco_access_token = ''
	s_cisco_sn_status = ''
	if c_cisco_login_error == 0:
		s_cisco_access_token = d_cisco_login_response['access_token']
		# s_cisco_refresh_token = d_cisco_login_response['refresh_token']

		url = 'https://swapi.cisco.com/services/api/software/dms/v2/smartaccounts/%s/virtualaccounts/%s/devices?startIdx=0&rowsPerPage=500' % (d_conf['cisco_smart_account'], d_conf['cisco_virtual_account'])
		headers = {'Authorization': 'Bearer %s' % s_cisco_access_token}
		r = s_cisco_session.get(url=url, headers=headers, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_cisco_sn_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_cisco_sn_error_message, indent=2, sort_keys=True))
			exit()
		d_cisco_sn_status = json.loads(r.content.decode('utf8'))

		s_cisco_sn_status = ''
		for s_cisco_sn in d_cisco_sn_status['data']:
			if s_vedge_sn == s_cisco_sn['udiSerialNumber']:
				print('\n')
				print(' SN:', s_cisco_sn['udiSerialNumber'], '  STATUS:', s_cisco_sn['deviceStatus'], '  LOCKED:',
				      s_cisco_sn['isLocked'])
				print('\n')
				s_cisco_sn_status = s_cisco_sn['udiSerialNumber']
	return s_cisco_access_token, s_cisco_sn_status

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	print('\n')
	gs_vedge_sn = input('  vEdge serial number: ')
	print('\n')
	os.system("clear")
	gs_cisco_access_token, gs_cisco_sn_status = smart_account_verify_serial_number__verification(gd_conf, gs_vedge_sn)
