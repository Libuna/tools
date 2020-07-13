#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import authentication
import os
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- verify template  --- #
def template_detach__verify_template(s_session, d_conf, s_vedge_sn):
	os.system("clear")
	s_no_template = False
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_template_verify_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_template_verify_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_template_verify = json.loads(r.content.decode('utf8'))

	for s_vtv in d_vedge_template_verify['data']:
		if s_vedge_sn in s_vtv['uuid']:
			if 'template' not in s_vtv.keys():
				print("\n")
				print(' ',s_vedge_sn, 'has no template assigned.\n')
				s_no_template = True
			if 'system-ip' in s_vtv.keys():
				s_vedge_ip = s_vtv['system-ip']
			else:
				s_vedge_ip = '--'

			return s_vedge_ip, s_no_template

# --- detach template --- #
def template_detach__detach_template(s_session, d_conf, s_vedge_sn, s_vedge_ip):
	d_vedge_template_detach = {"deviceType":"vedge","devices":[{"deviceId":s_vedge_sn,"deviceIP":s_vedge_ip}]}
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/config/device/mode/cli'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_vedge_template_detach)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_template_detach_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_template_detach_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_template_detach = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_vedge_template, indent=2, sort_keys=True))
	s_template_detach_config_id = d_vedge_template_detach['id']
	print("\n")
	print(' ', s_template_detach_config_id, '\n')

	c_tasks_status = 0
	s_template_detach_status = ''
	while c_tasks_status < 1:
		c_tasks_status = 0
		time.sleep(30)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/status/' + s_template_detach_config_id
		r = s_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vedge_detach_status_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vedge_detach_status_error_message, indent=2, sort_keys=True))
			exit()
		d_vedge_template_detach_status = json.loads(r.content.decode('utf8'))

		for s_vtds in d_vedge_template_detach_status['data']:
			if 'Success' in s_vtds['status'] or 'Done - Scheduled' in s_vtds['status'] or 'Fail' in s_vtds['status']:
				c_tasks_status += 1
			os.system("clear")
			l_status_char_len = []
			l_status_char_len.append(len(s_vtds['action']))
			l_status_char_len.append(len(s_vtds['currentActivity']))
			l_status_char_len.append(len(s_vtds['status']))
			l_status_char_len = sorted(l_status_char_len, reverse=True)
			print(2 * '\n')
			print('  ========= ', l_status_char_len[0] * '=')
			print('  action:   ', s_vtds['action'])
			print('  activity: ', s_vtds['currentActivity'])
			print('  status:   ', s_vtds['status'])
			print('  ========= ', l_status_char_len[0] * '=')
			del l_status_char_len[:]
			s_template_detach_status = s_vtds['status']
	print("\n")
	return s_template_detach_status

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	print("\n")
	gs_vedge_sn = input('  Serial number: ')
	gs_vedge_sn = gs_vedge_sn.strip()

	gs_vedge_ip, gs_no_template = template_detach__verify_template(gs_session, gd_conf, gs_vedge_sn)
	if gs_no_template is False:
		gs_template_detach_status = template_detach__detach_template(gs_session, gd_conf, gs_vedge_sn, gs_vedge_ip)


