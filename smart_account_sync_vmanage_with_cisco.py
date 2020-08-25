#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  informe@email.cz             #

import authentication
import os
import time
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Sync smart account --- #
def smart_account_sync_vmanage_with_cisco__sync_smart_account(s_session, d_conf):
	os.system("clear")
	d_sync_login = {"username": d_conf['cisco_username'], "password": d_conf['cisco_password'],
	                "validity_string": "valid"}
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/smartaccount/sync'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_sync_login)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_sync_smart_account_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_sync_smart_account_error_message, indent=2, sort_keys=True))
		exit()
	d_sync_smart_account = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_vedge_os_upgrade, indent=2, sort_keys=True))
	s_push_sync_smart_account = d_sync_smart_account['processId']
	print("\n")
	print(' ', s_push_sync_smart_account, '\n')

	c_tasks_status = 0
	while c_tasks_status < 1:
		c_tasks_status = 0
		time.sleep(30)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/status/' + s_push_sync_smart_account
		r = gs_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_sync_smartaccount_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_sync_smartaccount_error_message, indent=2, sort_keys=True))
			exit()
		d_sync_smart_account_status = json.loads(r.content.decode('utf8'))

		for s_vss in d_sync_smart_account_status['data']:
			if 'Success' in s_vss['status'] or 'Fail' in s_vss['status']:
				c_tasks_status += 1
			os.system("clear")
			l_status_char_len = []
			l_status_char_len.append(len(s_vss['action']))
			l_status_char_len.append(len(s_vss['currentActivity']))
			l_status_char_len.append(len(s_vss['status']))
			l_status_char_len = sorted(l_status_char_len, reverse=True)
			print(2 * '\n')
			print('  ========= ', l_status_char_len[0] * '=')
			print('  action:   ', s_vss['action'])
			print('  activity: ', s_vss['currentActivity'])
			print('  status:   ', s_vss['status'])
			print('  ========= ', l_status_char_len[0] * '=')
			del l_status_char_len[:]
	print("\n")

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	smart_account_sync_vmanage_with_cisco__sync_smart_account(gs_session, gd_conf)
