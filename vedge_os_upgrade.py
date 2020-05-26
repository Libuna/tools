#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  informe@email.cz             #

import vmanage_authentication
import os
import re
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## --- vedge serial number  --- ##
def vedge_serial():
	os.system("clear")
	print('')
	url = 'https://' + gs_vmanage_ip + '/dataservice/system/device/vedges'
	r = gs_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_serial_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_serial_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_serial = json.loads(r.content.decode('utf8'))

	l_vedge_serial = []
	d_vedge_ip = {}
	for s_vsv in d_vedge_serial['data']:
		if 'version' in s_vsv.keys():
			if gs_vedge_os_version not in s_vsv['version']:
				l_vedge_serial.append(s_vsv['uuid'])
				if 'system-ip' in s_vsv.keys():
					d_vedge_ip.update({s_vsv['uuid']: s_vsv['system-ip']})

	l_vedge_serial.sort()
	print('\n')
	print("  vEdge serial numbers:\n")

	c_vedge_serial = len(l_vedge_serial)
	n = 0
	nt = 1
	while nt <= c_vedge_serial:
		if n + 3 <= c_vedge_serial:
			s_vedge_serial = '  {:<40}{:<40}{:<40}'.format(l_vedge_serial[n], l_vedge_serial[n + 1],
			                                               l_vedge_serial[n + 2])
			print(s_vedge_serial)
			nt = nt + 3
			n = n + 3
		elif n + 2 <= c_vedge_serial:
			s_vedge_serial = '  {:<40}{:<40}'.format(l_vedge_serial[n], l_vedge_serial[n + 1])
			print(s_vedge_serial)
			nt = nt + 2
			n = n + 2
		elif n + 1 <= c_vedge_serial:
			s_vedge_serial = '  {:<40}'.format(l_vedge_serial[n])
			print(s_vedge_serial)
			nt = nt + 4

	print("\n")
	print("  >> Choose vEdge serial number to be upgraded with OS version %s: <<" % gs_vedge_os_version)
	print("  => ", end="")
	s_vedge_serial_i = input()
	s_vedge_serial_i = s_vedge_serial_i.strip()
	n = 0
	for s_vs in l_vedge_serial:
		s_vs = s_vs.strip()
		s_vs_re = re.search('^' + re.escape(s_vedge_serial_i) + '$', s_vs)
		if s_vs_re is not None:
			n = n + 1

	while n is 0:
		print("  !! Serial number doesn't match. Type again: !!")
		print("  => ", end="")
		s_vedge_serial_i = input()
		s_vedge_serial_i = s_vedge_serial_i.strip()
		for s_vs in l_vedge_serial:
			s_vs = s_vs.strip()
			s_vs_re = re.search('^' + re.escape(s_vedge_serial_i) + '$', s_vs)
			if s_vs_re is not None:
				n = n + 1

	s_vedge_ip = ''
	for k, v in d_vedge_ip.items():
		if s_vedge_serial_i in k:
			s_vedge_ip = v
	return s_vedge_serial_i, s_vedge_ip


# --- vedge OS upgrade --- #

def vedge_os_upgrade():
	d_template_os_upgrade = {"action": "install", "input": {"vEdgeVPN": 0, "vSmartVPN": 0,
	                                                        "data": [{"family": "vedge-mips",
	                                                                  "version": gs_vedge_os_version}],
	                                                        "versionType": "vmanage", "reboot": True, "sync": True},
	                         "devices": [{"deviceIP": gs_vedge_ip, "deviceId": gs_vedge_serial}], "deviceType": "vedge"}

	url = 'https://' + gs_vmanage_ip + '/dataservice/device/action/install'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_template_os_upgrade)
	r = gs_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_os_upgrade_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_os_upgrade_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_os_upgrade = json.loads(r.content.decode('utf8'))
	s_push_software_install_id = d_vedge_os_upgrade['id']
	print("\n")
	print('  ', s_push_software_install_id, '\n')

	c_tasks_status = 0
	while c_tasks_status < 1:
		c_tasks_status = 0
		time.sleep(30)
		url = 'https://' + gs_vmanage_ip + '/dataservice/device/action/status/' + s_push_software_install_id
		r = gs_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vedge_os_upgrade_status_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vedge_os_upgrade_status_error_message, indent=2, sort_keys=True))
			exit()
		d_vedge_os_upgrade_status = json.loads(r.content.decode('utf8'))

		for s_vous in d_vedge_os_upgrade_status['data']:
			if 'Success' in s_vous['status'] or 'Fail' in s_vous['status']:
				c_tasks_status += 1
			os.system("clear")
			l_status_char_len = []
			l_status_char_len.append(len(s_vous['action']))
			l_status_char_len.append(len(s_vous['currentActivity']))
			l_status_char_len.append(len(s_vous['status']))
			l_status_char_len = sorted(l_status_char_len, reverse=True)
			print(2 * '\n')
			print('  ========= ', l_status_char_len[0] * '=')
			print('  action:   ', s_vous['action'])
			print('  activity: ', s_vous['currentActivity'])
			print('  status:   ', s_vous['status'])
			print('  ========= ', l_status_char_len[0] * '=')
			del l_status_char_len[:]

	print("\n")


# --- main menu --- #
os.system("clear")
gs_vmanage_ip, gs_vmanage_username, gs_vmanage_password, gs_session, gs_email, gs_vedge_os_version, gj_uinfo = vmanage_authentication.login()
gs_vedge_serial, gs_vedge_ip = vedge_serial()
vedge_os_upgrade()
