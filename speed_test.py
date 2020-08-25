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
import itertools
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- source vedge --- #
def speed_test__source_vedge(s_session, d_conf):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_list_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_list_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_list = json.loads(r.content.decode('utf8'))
	l_source_vedge_list = []
	for s_vl in d_vedge_list['data']:
		if 'host-name' in s_vl.keys():
			l_source_vedge_list.append(s_vl['host-name'])

	l_source_vedge_list.sort()
	print('\n')
	print("  Source vEdge devices:\n")

	c_vedge_list = (len(l_source_vedge_list))
	c1 = int(c_vedge_list / 3)
	c2 = 3 * int(c1)
	if c2 < c_vedge_list:
		c1 = int(c1 + 1)

	a = (l_source_vedge_list[:c1])
	b = (l_source_vedge_list[c1:c1 + c1])
	c = (l_source_vedge_list[c1 + c1:])

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
	print("  >> Choose source vEdge (speed test will start from): <<")
	print("  => ", end="")
	s_vedge_name = input()
	s_vedge_name = s_vedge_name.strip()
	n = 0
	for s_vl in l_source_vedge_list:
		s_vl = s_vl.strip()
		s_vl_re = re.search('^' + re.escape(s_vedge_name) + '$', s_vl)
		if s_vl_re is not None:
			n = n + 1

	while n is 0:
		print("  !! vEdge name doesn't match. !!\n")
		print("  => ", end="")
		s_vedge_name = input()
		s_vedge_name = s_vedge_name.strip()
		for s_vl in l_source_vedge_list:
			s_vl = s_vl.strip()
			s_vl_re = re.search('^' + re.escape(s_vedge_name) + '$', s_vl)
			if s_vl_re is not None:
				n = n + 1

	s_source_vedge_name = ''
	s_source_vedge_sn = ''
	s_source_vedge_ip = ''
	s_source_vedge_reachable = ''
	for s_vl in d_vedge_list['data']:
		if 'host-name' in s_vl.keys():
			if s_vedge_name in s_vl['host-name']:
				s_source_vedge_name = s_vl['host-name']
				s_source_vedge_sn = s_vl['uuid']
				s_source_vedge_ip = s_vl['system-ip']
				s_source_vedge_reachable = s_vl['reachability']
	return s_source_vedge_name, s_source_vedge_sn, s_source_vedge_ip, s_source_vedge_reachable

# --- vedge pe peers (default gw) --- #
def speed_test__pe_ip(s_session, d_conf, s_vedge_ip):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/ip/routetable?deviceId=%s&vpn-id=0&&&' % s_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_pe_ip_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_pe_ip_error_message, indent=2, sort_keys=True))
		exit()
	d_pe_ip_all = json.loads(r.content.decode('utf8'))

	d_gateway_interface = {}
	for s_pia in d_pe_ip_all['data']:
		if ('0.0.0.0/0' in s_pia['prefix']) and ('static' in s_pia['protocol']):
			if 'nexthop-ifname' in s_pia.keys():
				d_gateway_interface.update({s_pia['nexthop-ifname']: s_pia['nexthop-addr']})
	return d_gateway_interface

# --- vEdge colors  --- #
def speed_test__colors(s_session, d_conf, s_source_vedge_ip, d_gateway_interface):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/control/waninterface?deviceId=' + s_source_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_colors_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_colors_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_colors_all = json.loads(r.content.decode('utf8'))

	c_vedge_color = 0
	d_vedge_colors = {}
	for s_vc in d_vedge_colors_all['data']:
		for s_gi in d_gateway_interface:
			s_vc_re = re.search('^' + s_gi + '$', s_vc['interface'])
			if s_vc_re and 'up' in s_vc['operation-state']:
				c_vedge_color += 1
				d_vedge_colors.update({str(c_vedge_color):s_vc['color']})

	if c_vedge_color == 1:
		s_vedge_color = d_vedge_colors['1']

	else:
		print('\n')
		for k, v in d_vedge_colors.items():
			print('  ', k, '. ', v)

		print(' ')
		print("  Choose vEdge source color (press a number):")
		print("  => ", end="")
		s_color_number = input()
		s_color_number.strip()

		while not s_color_number in d_vedge_colors.keys():
			print("  >> Wrong answer. Please try again: <<\n")
			print("  => ", end="")
			s_color_number = input()
			s_color_number.strip()

		s_vedge_color = d_vedge_colors[s_color_number]
	return s_vedge_color

# --- bfd sessions --- #
def speed_test__bfd_sessions(s_session, d_conf, s_source_vedge_ip, s_source_vedge_color):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/bfd/sessions?deviceId=%s&&&' % s_source_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_bfd_sessions_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_bfd_sessions_error_message, indent=2, sort_keys=True))
		exit()
	d_bfd_sessions = json.loads(r.content.decode('utf8'))

	l_destination_vedge_ips = []
	for s_bs in d_bfd_sessions['data']:
		if 'system-ip' in s_bs.keys() and 'color' in s_bs.keys() and 'local-color' in s_bs.keys():
			if s_source_vedge_color in s_bs['color'] and s_source_vedge_color in s_bs['local-color']:
				l_destination_vedge_ips.append(s_bs['system-ip'])
	return l_destination_vedge_ips

# --- destination vedge --- #
def speed_test__destination_vedge(s_session, d_conf, l_destination_vedge_ips):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_list_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_list_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_list = json.loads(r.content.decode('utf8'))

	l_destination_vedge_list = []
	for s_dvl in l_destination_vedge_ips:
		for s_vl in d_vedge_list['data']:
			if 'system-ip' in s_vl.keys():
				s_ip_re = re.search('^'+s_dvl+'$', s_vl['system-ip'])
				if s_ip_re:
					l_destination_vedge_list.append(s_vl['host-name'])

	l_destination_vedge_list.sort()
	print('\n')
	print("  Destination vEdge devices:\n")

	c_vedge_list = (len(l_destination_vedge_list))
	c1 = int(c_vedge_list / 3)
	c2 = 3 * int(c1)
	if c2 < c_vedge_list:
		c1 = int(c1 + 1)

	a = (l_destination_vedge_list[:c1])
	b = (l_destination_vedge_list[c1:c1 + c1])
	c = (l_destination_vedge_list[c1 + c1:])

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
	print("  >> Choose destination vEdge (speed test will connect to): <<")
	print("  => ", end="")
	s_vedge_name = input()
	s_vedge_name = s_vedge_name.strip()
	n = 0
	for s_vl in l_destination_vedge_list:
		s_vl = s_vl.strip()
		s_vl_re = re.search('^' + re.escape(s_vedge_name) + '$', s_vl)
		if s_vl_re is not None:
			n = n + 1

	while n is 0:
		print("  !! vEdge name doesn't match. !!\n")
		print("  => ", end="")
		s_vedge_name = input()
		s_vedge_name = s_vedge_name.strip()
		for s_vl in l_destination_vedge_list:
			s_vl = s_vl.strip()
			s_vl_re = re.search('^' + re.escape(s_vedge_name) + '$', s_vl)
			if s_vl_re is not None:
				n = n + 1

	s_destination_vedge_name = ''
	s_destination_vedge_sn = ''
	s_destination_vedge_ip = ''
	s_destination_vedge_reachable = ''
	for s_vl in d_vedge_list['data']:
		if 'host-name' in s_vl.keys():
			if s_vedge_name in s_vl['host-name']:
				s_destination_vedge_name = s_vl['host-name']
				s_destination_vedge_sn = s_vl['uuid']
				s_destination_vedge_ip = s_vl['system-ip']
				s_destination_vedge_reachable = s_vl['reachability']
	return s_destination_vedge_name, s_destination_vedge_sn, s_destination_vedge_ip, s_destination_vedge_reachable

# --- speedtest parameters --- #
def speed_test__parameters(s_session, d_conf, s_source_vedge_ip, s_source_vedge_sn, s_destination_vedge_ip, s_vedge_color):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/stream/device/speed'
	speedtest = {"deviceUUID":"none", "sourceIp":"none", "sourceColor":"none", "destinationIp":"none", "destinationColor":"none", "port":"80"}
	speedtest.update({'deviceUUID': s_source_vedge_sn})
	speedtest.update({'sourceIp': s_source_vedge_ip})
	speedtest.update({'sourceColor': s_vedge_color})
	speedtest.update({'destinationIp': s_destination_vedge_ip})
	speedtest.update({'destinationColor': s_vedge_color})

	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(speedtest)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_speedtest_parameters_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_speedtest_parameters_error_message, indent=2, sort_keys=True))
		exit()
	d_speedtest_parameters = json.loads(r.content.decode('utf8'))
	print('\n')
	print('  vEdge speed test parameters sent to vManage. Testing color: ', s_vedge_color, '\n')
	s_speed_session_id = d_speedtest_parameters['sessionId']
	print('  session id:  ', s_speed_session_id, '\n')

	gl_speed_test_results.append('\n')
	gl_speed_test_results.append('  vEdge speed test parameters sent to vManage. Testing color: ' + s_vedge_color + '\n')
	gl_speed_test_results.append('  session id:  ' + s_speed_session_id + '\n')

	return s_speed_session_id

# --- speed test start --- #
def speed_test__start(s_session, d_conf, s_speed_session_id):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/stream/device/speed/start/' + s_speed_session_id
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_speedtest_start_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_speedtest_start_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_speedtest_start = json.loads(r.content.decode('utf8'))

	if 'status' in d_vedge_speedtest_start:
		print('  vEdge speed test started: ', d_vedge_speedtest_start['status'], '\n')
		gl_speed_test_results.append('  vEdge speed test started: ' + d_vedge_speedtest_start['status'] + '\n')
		if 'fail' in d_vedge_speedtest_start['status']:
			print('  Session belongs to different owner, test in progress by different user hence not able run it now.\n')
			gl_speed_test_results.append('  Session belongs to different owner, test in progress by different user hence not able run it now.\n')
			s_speedtest_status_fail = 'fail'
			return s_speedtest_status_fail

# --- speedtest live results --- #
def speed_test__live_results(s_session, d_conf, s_speed_session_id, s_source_vedge_ip):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/stream/device/speed/%s'% s_speed_session_id + '?logId=3'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_speedtest_output_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_speedtest_output_error_message, indent=2, sort_keys=True))
		speed_test__stop(s_session, d_conf, s_speed_session_id)
		exit()
	d_vedge_speedtest_output_up_down = json.loads(r.content.decode('utf8'))

	for s_vsoud in d_vedge_speedtest_output_up_down['data']:
		if s_vsoud['status']:
			print(' ')
			print('  vEdge speed test results from live session:\n')
			print('  bw-down:    ', s_vsoud['down_bw'], ' Kbps')
			print('  bw-up:      ', s_vsoud['up_bw'], ' Kbps')
			print('  speed-down: ', s_vsoud['down_speed'], ' Mbps')
			print('  speed-up:   ', s_vsoud['up_speed'], ' Mbps')
			print('  dst-ip:     ', s_vsoud['destination_ip'])
			print('  status:     ', s_vsoud['status'], '\n')
			gl_speed_test_results.append('  vEdge speed test results from live session:\n')
			gl_speed_test_results.append('  bw-down:    ' + str(s_vsoud['down_bw']) + ' Kbps')
			gl_speed_test_results.append('  bw-up:      ' + str(s_vsoud['up_bw']) + ' Kbps')
			gl_speed_test_results.append('  speed-down: ' + str(s_vsoud['down_speed']) + ' Mbps')
			gl_speed_test_results.append('  speed-up:   ' + str(s_vsoud['up_speed']) + ' Mbps')
			gl_speed_test_results.append('  dst-ip:     ' + str(s_vsoud['destination_ip']))
			gl_speed_test_results.append('  status:     ' + str(s_vsoud['status']) + '\n')
			gl_speed_test_results.append('\n')

	c_speedtest = 1
	while not d_vedge_speedtest_output_up_down['data'] and c_speedtest <= 25:
		print ('  ... ',c_speedtest,'/25', end='\r')
		gl_speed_test_results.append('  ... ' + str(c_speedtest) + '/25')
		c_speedtest += 1
		time.sleep(5)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/stream/device/speed/%s' % s_speed_session_id + '?logId=3'
		r = s_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vedge_speedtest_output_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vedge_speedtest_output_error_message, indent=2, sort_keys=True))
			speed_test__stop(s_session, d_conf, s_speed_session_id)
			exit()
		d_vedge_speedtest_output_up_down = json.loads(r.content.decode('utf8'))
		for s_vsoud in d_vedge_speedtest_output_up_down['data']:
			if s_vsoud['status']:
				print('\n')
				print('  vEdge speed test results from live session:\n')
				if 'down_bw' in s_vsoud:
					print('  bw-down:    ', s_vsoud['down_bw'], ' Kbps')
				if 'up_bw' in s_vsoud:
					print('  bw-up:      ', s_vsoud['up_bw'], ' Kbps')
				print('  speed-down: ', s_vsoud['down_speed'], ' Mbps')
				print('  speed-up:   ', s_vsoud['up_speed'], ' Mbps')
				print('  dst-ip:     ', s_vsoud['destination_ip'])
				print('  status:     ', s_vsoud['status'], '\n')
				gl_speed_test_results.append('\n')
				gl_speed_test_results.append('  vEdge speed test results from live session:\n')
				if 'down_bw' in s_vsoud:
					gl_speed_test_results.append('  bw-down:    ' + str(s_vsoud['down_bw']) + ' Kbps')
				if 'up_bw' in s_vsoud:
					gl_speed_test_results.append('  bw-up:      ' + str(s_vsoud['up_bw']) + ' Kbps')
				gl_speed_test_results.append('  speed-down: ' + str(s_vsoud['down_speed']) + ' Mbps')
				gl_speed_test_results.append('  speed-up:   ' + str(s_vsoud['up_speed']) + ' Mbps')
				gl_speed_test_results.append('  dst-ip:     ' + str(s_vsoud['destination_ip']))
				gl_speed_test_results.append('  status:     ' + str(s_vsoud['status']) + '\n')

	if c_speedtest > 25:
		print('  vEdge speed test did not finish in time\n')
		gl_speed_test_results.append('\n')
		gl_speed_test_results.append('  vEdge speed test did not finish in time\n')
	return c_speedtest

# --- speedtest stop --- #
def speed_test__stop(s_session, d_conf, s_speed_session_id):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/stream/device/speed/disable/' + s_speed_session_id
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_speedtest_stop_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_speedtest_stop_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_speedtest_stop = json.loads(r.content.decode('utf8'))
	print(' ')
	print('  vEdge speed test stopped: ', d_vedge_speedtest_stop['status'])
	print(2 * "\n")
	gl_speed_test_results.append('  vEdge speed test stopped: ' + d_vedge_speedtest_stop['status'])
	gl_speed_test_results.append('\n')
	gl_speed_test_results.append('\n')

# --- speedtest history results --- #
def speed_test__history_results(s_session, d_conf, s_source_vedge_ip, s_speed_session_id):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/statistics/speedtest'
	speed_history = {"query":{"condition":"AND","rules":[{"value":["none"],"field":"source_local_ip","type":"string","operator":"in"},{"value":["completed"],"field":"status","type":"string","operator":"in"}]},"size":10000}
	for s_sh in speed_history['query']['rules']:
		s_sh['value'] = [s_source_vedge_ip]
		break
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(speed_history)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_error_message, indent=2, sort_keys=True))
		speed_test__stop(s_session, d_conf, s_speed_session_id)
		exit()
	d_vedge_speedtest_history = json.loads(r.content.decode('utf8'))

	gl_speed_test_results.append('\n')
	gl_speed_test_results.append('\n')

	if d_vedge_speedtest_history['data']:
		print('  vEdge speed test results from older session:\n')
		gl_speed_test_results.append('  vEdge speed test results from older session:\n')
		gl_speed_test_results.append('\n')
	for s_vsh in d_vedge_speedtest_history['data']:
		if s_vsh['status']:
			print('  download:   ', s_vsh['down_speed'])
			print('  upload:     ', s_vsh['up_speed'], '\n')
			gl_speed_test_results.append('  download:   ' + str(s_vsh['down_speed']))
			gl_speed_test_results.append('  upload:     ' + str(s_vsh['up_speed']) + '\n')

def speed_test__tracker():
	return gl_speed_test_results

# --- main menu --- #
os.system("clear")
gl_speed_test_results = []
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	gs_source_vedge_name, gs_source_vedge_sn, gs_source_vedge_ip, gs_source_vedge_reachable = speed_test__source_vedge(gs_session, gd_conf)
	if not 'unreachable' in gs_source_vedge_reachable:
		gd_gateway_interface = speed_test__pe_ip(gs_session, gd_conf, gs_source_vedge_ip)
		gs_vedge_color = speed_test__colors(gs_session, gd_conf, gs_source_vedge_ip, gd_gateway_interface)
		gl_destination_vedge_ips = speed_test__bfd_sessions(gs_session, gd_conf, gs_source_vedge_ip, gs_vedge_color)
		gs_destination_vedge_name, gs_destination_vedge_sn, gs_destination_vedge_ip, gs_destination_vedge_reachable = speed_test__destination_vedge(gs_session, gd_conf, gl_destination_vedge_ips)

		# if not 'unreachable' in gs_source_vedge_reachable and not 'unreachable' in gs_destination_vedge_reachable:
		# 	gs_speed_session_id = speed_test__parameters(gs_session, gd_conf, gs_source_vedge_ip, gs_source_vedge_sn, gs_destination_vedge_ip, gs_vedge_color)
		# 	gs_speedtest_status_fail = speed_test__start(gs_session, gd_conf, gs_speed_session_id)
		# 	if not gs_speedtest_status_fail:
		# 		gc_speedtest = speed_test__live_results(gs_session, gd_conf, gs_speed_session_id, gs_source_vedge_ip)
		# 		if gc_speedtest > 25:
		# 			speed_test__history_results(gs_session, gd_conf, gs_source_vedge_ip, gs_speed_session_id)
		# 	else:
		# 		speed_test__history_results(gs_session, gd_conf, gs_source_vedge_ip, gs_speed_session_id)
		# 	speed_test__stop(gs_session, gd_conf, gs_speed_session_id)
		#
		# else:
		# 	print("\n")
		# 	print("  Destination vEdge is unreachable in vManage")
		# 	print("\n")

	else:
		print("\n")
		print("  Source vEdge is unreachable in vManage")
		print("\n")

