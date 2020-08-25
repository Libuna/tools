#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import authentication
import os
import re
import sys
import json
import time
import select
import urllib3
import itertools
from colorama import Fore, Back, Style
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- vedge serial number --- #
def template_attach__vedge_serials(s_session, d_conf):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges'
	r = s_session.get(url=url, verify=False)
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
	l_vedge_sn_name = []
	d_vedge_name = {}
	for s_vsv in d_vedge_serial['data']:
		if 'templateId' not in s_vsv.keys() and 'cli' in s_vsv['configOperationMode']:
			l_vedge_serial.append(s_vsv['uuid'])
			if 'host-name' in s_vsv.keys():
				d_vedge_name.update({s_vsv['uuid']: s_vsv['host-name']})

	print('\n')
	print("  vEdge name or serial number:\n")

	for s_vs in l_vedge_serial:
		if s_vs in d_vedge_name.keys():
			l_vedge_sn_name.append(d_vedge_name[s_vs])
		else:
			l_vedge_sn_name.append(s_vs)

	l_vedge_sn_name.sort()
	c_vedge_sn_name = len(l_vedge_sn_name)
	c1 = int(c_vedge_sn_name / 3)
	c2 = 3 * int(c1)
	if c2 < c_vedge_sn_name:
		c1 = int(c1 + 1)

	a = (l_vedge_sn_name[:c1])
	b = (l_vedge_sn_name[c1:c1 + c1])
	c = (l_vedge_sn_name[c1 + c1:])

	for x, y, z in itertools.zip_longest(a, b, c):
		if x and y and z:
			s_vedge_list = '  {:<42}{:<42}{:<42}'.format(x, y, z)
			print(s_vedge_list)
		elif x and y:
			s_vedge_list = '  {:<42}{:<42}'.format(x, y)
			print(s_vedge_list)
		else:
			s_vedge_list = '  {:<42}'.format(x)
			print(s_vedge_list)

	print("\n")
	print("  >> Choose vEdge name or serial number to be attached into template: <<")
	print("  => ", end="")
	s_vedge_sn_name_i = input()
	s_vedge_sn_name_i = s_vedge_sn_name_i.strip()
	n = 0
	for s_vsn in l_vedge_sn_name:
		s_vsn = s_vsn.strip()
		s_vsn_re = re.search('^' + re.escape(s_vedge_sn_name_i) + '$', s_vsn)
		if s_vsn_re is not None:
			n = n + 1

	while n is 0:
		print("  !! Name or serial number doesn't match. Type again: !!\n")
		print("  => ", end="")
		s_vedge_sn_name_i = input()
		s_vedge_sn_name_i = s_vedge_sn_name_i.strip()
		for s_vsn in l_vedge_sn_name:
			s_vsn = s_vsn.strip()
			s_vsn_re = re.search('^' + re.escape(s_vedge_sn_name_i) + '$', s_vsn)
			if s_vsn_re is not None:
				n = n + 1

	for k, v in d_vedge_name.items():
		if s_vedge_sn_name_i in v:
			s_vedge_sn_name_i = k
	return s_vedge_sn_name_i

# --- vedge templates --- #
def template_attach__template_list(s_session, d_conf):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_template_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_template_error_message, indent=2, sort_keys=True))
		exit()
	d_template = json.loads(r.content.decode('utf8'))
	l_template = []
	for s_t in d_template['data']:
		if 'templateName' in s_t.keys():
			l_template.append(s_t['templateName'])

		l_template.sort()
	print('\n')
	print("  vEdge templates:\n")

	c_template = (len(l_template))
	c1 = int(c_template / 3)
	c2 = 3 * int(c1)
	if c2 < c_template:
		c1 = int(c1 + 1)

	a = (l_template[:c1])
	b = (l_template[c1:c1 + c1])
	c = (l_template[c1 + c1:])

	for x, y, z in itertools.zip_longest(a, b, c):
		if x and y and z:
			s_template = '  {:<42}{:<42}{:<42}'.format(x, y, z)
			print(s_template)
		elif x and y:
			s_template = '  {:<42}{:<42}'.format(x, y)
			print(s_template)
		else:
			s_template = '  {:<42}'.format(x)
			print(s_template)

	print("\n")
	print("  >> Choose template to be attached into vEdge: <<")
	print("  => ", end="")
	s_template_i = input()
	s_template_i = s_template_i.strip()
	n = 0
	for s_t in l_template:
		s_t = s_t.strip()
		s_t_re = re.search('^' + re.escape(s_template_i) + '$', s_t)
		if s_t_re is not None:
			n = n + 1

	while n is 0:
		print("  !! Template name doesn't match. Type again: !!")
		print("  => ", end="")
		s_template_i = input()
		s_template_i = s_template_i.strip()
		for s_t in l_template:
			s_t = s_t.strip()
			s_t_re = re.search('^' + re.escape(s_template_i) + '$', s_t)
			if s_t_re is not None:
				n = n + 1

	s_template_id = ''
	for s_t in d_template['data']:
		s_t_re = re.search('^' + re.escape(s_template_i) + '$', s_t['templateName'])
		if s_t_re:
			s_template_id = s_t['templateId']

	return l_template, s_template_id


# --- update template --- #
def template_attach__update_template(s_session, d_conf, s_vedge_sn, s_vedge_template_id):
	l_template_deviceid = []
	l_template_deviceid.append(s_vedge_sn)
	d_template_deviceid = {"templateId":"none","deviceIds":["none"],"isEdited":False,"isMasterEdited":False}
	d_template_deviceid.update({"templateId":s_vedge_template_id})
	d_template_deviceid.update({"deviceIds":l_template_deviceid})
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device/config/input/'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_template_deviceid)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_template_variables_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_template_variables_error_message, indent=2, sort_keys=True))
		exit()
	d_template_variables = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_vedge_template, indent=2, sort_keys=True))
	os.system("clear")

	c_template_value_update = 0
	for s_tv in d_template_variables['data']:
		for k, v in s_tv.items():
			v_re = re.search('\w+|!', v)
			if 'csv-' not in k:
				if not v_re:
					c_template_value_update += 1

	if c_template_value_update == 0:
		print("""


			ALL MANDATORY TEMPLATE VALUES AVAILABLE:

			""")



	else:
		print(Back.RED + Fore.WHITE + """

	Copy all the below mandatory keys to notepad and fill all the values right after a key ":===>".
	Paste all the keys with filled values back to prompt and press "Ctrl+d".

	E.g:
	HOSTNAME:===>konecr-device1
	SYSTEM_IP:===>192.168.55.55
	SITE_ID:===>808333
	etc...

	press Ctrl+d

	""")
		print(Style.RESET_ALL)



	c_template_variables = 0
	c_template_variables_filled = 0
	d_template_variables_update = {}
	for s_tv in d_template_variables['data']:
		for k, v in s_tv.items():
			v_re = re.search('\w+|!', v)
			if 'csv-' not in k:
				if not v_re:
					# s_value_update = '  {:<93}{:<5}'.format(k,':===>')
					# print(s_value_update)
					print('  ' + Back.BLUE + Fore.WHITE + k + Style.RESET_ALL + ':===>')
					c_template_variables += 1
				else:
					d_template_variables_update.update({k:v})
			if 'csv' in k:
				d_template_variables_update.update({k:v})
			if 'csv-status' in k:
				d_template_variables_update.update({k:"complete"})
			d_template_variables_update.update({"csv-templateId":s_vedge_template_id})


	if c_template_variables > 0:
		print('\n')
		print('  Paste the filled keys and values and press "Ctrl+d"')
		print('  =>:')
		s_readlines = ''
		i, o, e = select.select([sys.stdin], [], [], 600)
		if (i):
			s_readlines = sys.stdin.readlines()
		else:
			print('')
			print('  Timeout ...')
			print('')
			exit()

		for s_rl in s_readlines:
			s_rl_re = re.search('^\n', s_rl)
			if s_rl_re:
				continue
			s_rl = s_rl.strip()
			s_rl_re = re.search(':===>', s_rl)
			if s_rl_re:
				c_template_variables_filled += 1
				s_rl = s_rl.replace('\n', '')
				l_rl = s_rl.split(':===>')

				l_rl[0] = l_rl[0].rstrip()
				if l_rl[1]:
					l_rl[1] = l_rl[1].rstrip()
				d_template_variables_update.update({l_rl[0]:l_rl[1]})
				s_value_re = re.search(r'\w+|!', l_rl[1])
				while not s_value_re:
					print('')
					print("  Missing value, please provide:")
					s_value_i = input('  ' + l_rl[0] + ' :====> ')
					s_value_i = s_value_i.strip()
					s_value_re = re.search(r'\w+|!', s_value_i)
					d_template_variables_update.update({l_rl[0]:s_value_i})
			else:
				continue

	print('\n')
	d_template_form_updated = {
		"deviceTemplateList":[{"templateId":s_vedge_template_id,
		                        "device":[d_template_variables_update], "isEdited":False}]}

	if c_template_variables == c_template_variables_filled:
		return d_template_form_updated
	else:
		os.system("clear")
		print('\n')
		message = "  Variables in template don't match with variables provided. \n"
		print(message)

# --- attach template --- #
def template_attach__attach_template(s_session, d_conf, d_template_form_updated):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device/config/attachcli'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_template_form_updated)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_template_form_preview_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_template_form_preview_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_template_form_preview = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_vedge_template_form_preview, indent=2, sort_keys=True))
	s_push_file_template_id = d_vedge_template_form_preview['id']
	print("\n")
	print(' ', s_push_file_template_id, '\n')

	c_tasks_status = 0
	s_template_attach_status = ''
	while c_tasks_status < 1:
		c_tasks_status = 0
		time.sleep(10)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/status/' + s_push_file_template_id
		r = s_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vmanage_assign_template_status_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vmanage_assign_template_status_error_message, indent=2, sort_keys=True))
			exit()
		d_vmanage_assign_template_status = json.loads(r.content.decode('utf8'))

		for s_vats in d_vmanage_assign_template_status['data']:
			if 'Success' in s_vats['status'] or 'Done - Scheduled' in s_vats['status'] or 'Fail' in s_vats[
				'status']:
				c_tasks_status += 1
			os.system("clear")
			l_status_char_len = []
			l_status_char_len.append(len(s_vats['action']))
			l_status_char_len.append(len(s_vats['currentActivity']))
			l_status_char_len.append(len(s_vats['status']))
			l_status_char_len = sorted(l_status_char_len, reverse=True)
			print(2 * '\n')
			print('  ========= ', l_status_char_len[0] * '=')
			print('  action:   ', s_vats['action'])
			print('  activity: ', s_vats['currentActivity'])
			print('  status:   ', s_vats['status'])
			print('  ========= ', l_status_char_len[0] * '=')
			del l_status_char_len[:]
			s_template_attach_status = s_vats['status']
	print("\n")
	return s_template_attach_status

# --- main --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	gs_vedge_sn = template_attach__vedge_serials(gs_session, gd_conf)
	gl_vedge_template, gs_vedge_template_id = template_attach__template_list(gs_session, gd_conf)
	gd_template_form_updated = template_attach__update_template(gs_session, gd_conf, gs_vedge_sn, gs_vedge_template_id)
	if gd_template_form_updated:
		gs_template_attach_status = template_attach__attach_template(gs_session, gd_conf, gd_template_form_updated)

