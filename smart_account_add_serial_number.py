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


# --- Cisco auth token request and add serial --- #
def smart_account_add_serial_number__add_serial(d_conf, s_vedge_sn):
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

	s_cisco_add_status = ''
	s_cisco_add_message = ''
	s_cisco_add_validation = ''
	s_cisco_add_description = ''
	if c_cisco_login_error == 0:
		s_cisco_access_token = d_cisco_login_response['access_token']
		# s_cisco_refresh_token = d_cisco_login_response['refresh_token']

		# --- Cisco add serial --- #
		print('\n')
		v100 = 'VEDGE-100B-AC-K9'
		v1000 = 'VEDGE-1000-AC-K9'
		v2000 = 'VEDGE-2000-AC-K9'
		print('  1. ', v100)
		print('  2. ', v1000)
		print('  3. ', v2000, '\n')
		s_cisco_vedge_model = input('  - Choose vEdge model (1-3): ')
		s_cisco_vedge_model = s_cisco_vedge_model.strip()
		s_cisco_vedge_model_re = re.search('^[1-3]$', s_cisco_vedge_model)
		while s_cisco_vedge_model_re is None:
			print("  ! Incorrect option !\n")
			s_cisco_vedge_model = input('  - Choose vEdge model (1-3): ')
			s_cisco_vedge_model = s_cisco_vedge_model.strip()
			s_cisco_vedge_model_re = re.search('^[1-3]$', s_cisco_vedge_model)
		if '1' in s_cisco_vedge_model:
			s_cisco_vedge_model = 'VEDGE-100B-AC-K9'
		if '2' in s_cisco_vedge_model:
			s_cisco_vedge_model = 'VEDGE-1000-AC-K9'
		if '3' in s_cisco_vedge_model:
			s_cisco_vedge_model = 'VEDGE-2000-AC-K9'
		url = 'https://swapi.cisco.com/services/api/software/dms/v2/smartaccounts/%s/virtualaccounts/%s/devices' % (d_conf['cisco_smart_account'], d_conf['cisco_virtual_account'])
		d_add_device = {"overWrite": False, "devices": [{"id": "1", "device": {
			"udi": [{"name": "udiProductId", "value": s_cisco_vedge_model},
			        {"name": "udiSerialNumber", "value": s_vedge_sn}]}}]}
		headers = {'Content-Type': "application/json", 'Authorization': 'Bearer %s' % s_cisco_access_token}
		payload = json.dumps(d_add_device)
		r = s_cisco_session.post(url=url, data=payload, headers=headers, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_cisco_add_device_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_cisco_add_device_error_message, indent=2, sort_keys=True))
			exit()
		d_cisco_add_device = json.loads(r.content.decode('utf8'))

		s_cisco_add_status = d_cisco_add_device['status']
		s_cisco_add_message = d_cisco_add_device['message']
		s_cisco_add_validation = ''
		s_cisco_add_description = ''
		for s_cad in d_cisco_add_device['devices']:
			s_cisco_add_validation = s_cad['validationStatus']
			s_cisco_add_description = s_cad['statusMessage']

	return s_cisco_add_status, s_cisco_add_message, s_cisco_add_validation, s_cisco_add_description

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	print('\n')
	gs_vedge_sn = input('  vEdge serial number: ')
	print('\n')
	os.system("clear")
	gs_cisco_add_status, gs_cisco_add_message, gs_cisco_add_validation, gs_cisco_add_description = smart_account_add_serial_number__add_serial(gd_conf, gs_vedge_sn)
	print('\n')
	print('  ' + gs_cisco_add_status)
	print('  ' + gs_cisco_add_message)
	print('  ' + gs_cisco_add_validation)
	print('  ' + gs_cisco_add_description)
	print('\n')

