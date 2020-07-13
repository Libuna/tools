#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  informe@email.cz             #

import authentication
import os
import re
import json
import time
import urllib3
import itertools
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- vedge serial  --- #
def image_default__vedge_serial(s_session, d_conf):
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
	d_vedge_ip = {}
	d_vedge_name = {}
	for s_vsv in d_vedge_serial['data']:
		if 'defaultVersion' in s_vsv.keys():
			if d_conf['vedge_image_version'] not in s_vsv['defaultVersion']:
				l_vedge_serial.append(s_vsv['uuid'])
				if 'system-ip' in s_vsv.keys():
					d_vedge_ip.update({s_vsv['uuid']:s_vsv['system-ip']})
				if 'host-name' in s_vsv.keys():
					d_vedge_name.update({s_vsv['uuid']: s_vsv['host-name']})

	print('\n')
	print("  vEdge serial numbers:\n")

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
	print("  >> Choose vEdge name or serial number: <<" )
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
		print("  !! Serial number doesn't match. Type again: !!")
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

	s_vedge_ip = ''
	for k,v in d_vedge_ip.items():
		if s_vedge_sn_name_i in k:
			s_vedge_ip = v
	return s_vedge_sn_name_i, s_vedge_ip

# --- set default partition --- #
def image_default__default_partition(s_session, d_conf, s_vedge_ip, s_vedge_sn):
	d_template_partition = {"action": "defaultpartition",
	 "devices": [{"version": d_conf['vedge_image_version'], "deviceIP": s_vedge_ip, "deviceId": s_vedge_sn}],
	 "deviceType": "vedge"}

	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/defaultpartition'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_template_partition)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_default_partition_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_default_partition_error_message, indent=2, sort_keys=True))
		exit()
	d_default_partition = json.loads(r.content.decode('utf8'))
	s_push_default_partition_id = d_default_partition['id']
	print("\n")
	print(' ',s_push_default_partition_id,'\n')

	c_tasks_status = 0
	s_image_default_status = ''
	while c_tasks_status < 1:
		c_tasks_status = 0
		time.sleep(10)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/status/' + s_push_default_partition_id
		r = gs_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_default_partition_status_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_default_partition_status_error_message, indent=2, sort_keys=True))
			exit()
		d_default_partition_status = json.loads(r.content.decode('utf8'))

		for s_vdps in d_default_partition_status['data']:
			if 'Success' in s_vdps['status'] or 'Fail' in s_vdps['status']:
				c_tasks_status += 1
			os.system("clear")
			l_status_char_len = []
			l_status_char_len.append(len(s_vdps['action']))
			l_status_char_len.append(len(s_vdps['currentActivity']))
			l_status_char_len.append(len(s_vdps['status']))
			l_status_char_len = sorted(l_status_char_len, reverse=True)
			print(2 * '\n')
			print('  ========= ', l_status_char_len[0] * '=')
			print('  action:   ', s_vdps['action'])
			print('  activity: ', s_vdps['currentActivity'])
			print('  status:   ', s_vdps['status'])
			print('  ========= ', l_status_char_len[0] * '=')
			del l_status_char_len[:]
			s_image_default_status = s_vdps['status']
	print("\n")
	return s_image_default_status

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	gs_vedge_sn, gs_vedge_ip = image_default__vedge_serial(gs_session, gd_conf)
	gs_image_default_status = image_default__default_partition(gs_session, gd_conf, gs_vedge_ip, gs_vedge_sn)
