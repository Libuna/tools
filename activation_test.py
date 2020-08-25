#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  informe@email.cz             #

import authentication
from speed_test import *
import os
import re
import json
import urllib3
import smtplib
import ipaddress
from datetime import datetime
from netmiko import ConnectHandler
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from colorama import Fore, Back, Style
from netmiko import NetMikoTimeoutException
from email.mime.multipart import MIMEMultipart
from netmiko import NetMikoAuthenticationException
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- source vedge --- #
def activation_test__source_vedge(s_session, d_conf, s_vedge_ip):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges?deviceIP=%s&' % s_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_serial_number_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_serial_number_error_message, indent=2, sort_keys=True))
		exit()
	d_serial_number = json.loads(r.content.decode('utf8'))

	for s_vsn in d_serial_number['data']:
		s_vedge_sn = s_vsn['uuid']
		s_vedge_name = s_vsn['host-name']
		s_vedge_reachable = s_vsn['reachability']

		return s_vedge_sn, s_vedge_name, s_vedge_reachable

# --- vedge interfaces (vpn, int, port-type) --- #
def activation_test__interfaces(s_session, d_conf, s_vedge_ip):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/interface?deviceId=%s&&&' % s_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_interfaces_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_interfaces_error_message, indent=2, sort_keys=True))
		exit()
	d_interfaces_all = json.loads(r.content.decode('utf8'))

	d_vpn0_interfaces = {}
	d_vpn0_interfaces_down = {}
	for s_ia in d_interfaces_all['data']:
		s_ia_re = re.search('ge\d+/\d+|10ge\d+/\d+|ppp\d+', s_ia['ifname'])
		s_ipaddress_re = re.sub(r"/\d+", '', s_ia['ip-address'])

		s_ip_address = ''
		try:
			s_ip_address = ipaddress.ip_address(s_ipaddress_re)
		except ValueError:
			pass

		if s_ia_re and s_ip_address and '0' in s_ia['vpn-id'] and 'ipv4' in s_ia['af-type'] and 'transport' in s_ia['port-type'] and 'Up' in s_ia['if-oper-status']:
			d_vpn0_interfaces[s_ia['ifname']] = ({'interface': s_ia['ifname']})
			d_vpn0_interfaces[s_ia['ifname']].update({'vpn-id': s_ia['vpn-id']})
			d_vpn0_interfaces[s_ia['ifname']].update({'port-type': s_ia['port-type']})
			d_vpn0_interfaces[s_ia['ifname']].update({'ip': s_ia['ip-address']})
			d_vpn0_interfaces[s_ia['ifname']].update({'if-admin-status': s_ia['if-admin-status']})
			d_vpn0_interfaces[s_ia['ifname']].update({'if-oper-status': s_ia['if-oper-status']})
		if s_ia_re and s_ip_address and '0' in s_ia['vpn-id'] and 'ipv4' in s_ia['af-type'] and 'transport' in s_ia['port-type'] and 'Down' in s_ia['if-oper-status']:
			d_vpn0_interfaces_down[s_ia['ifname']] = ({'interface': s_ia['ifname']})
			d_vpn0_interfaces_down[s_ia['ifname']].update({'vpn-id': s_ia['vpn-id']})
			d_vpn0_interfaces_down[s_ia['ifname']].update({'port-type': s_ia['port-type']})
			d_vpn0_interfaces_down[s_ia['ifname']].update({'ip': s_ia['ip-address']})
			d_vpn0_interfaces_down[s_ia['ifname']].update({'if-admin-status': s_ia['if-admin-status']})
			d_vpn0_interfaces_down[s_ia['ifname']].update({'if-oper-status': s_ia['if-oper-status']})
	return d_vpn0_interfaces, d_vpn0_interfaces_down

# --- vedge colors --- #
def activation_test__interface_color(s_session, d_conf, s_vedge_ip, d_vpn0_interfaces):
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/control/waninterface?deviceId=' + s_vedge_ip
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_interface_color_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_interface_color_error_message, indent=2, sort_keys=True))
		exit()
	d_interface_color_all = json.loads(r.content.decode('utf8'))

	for k in d_vpn0_interfaces.keys():
		for s_vi in d_interface_color_all['data']:
			if k in s_vi['interface']:
				d_vpn0_interfaces[s_vi['interface']].update({'color': s_vi['color']})

# --- vedge pe peers (default gw) --- #
def activation_test__pe_ip(s_session, d_conf, s_vedge_ip, d_vpn0_interfaces):
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

	for s_pia in d_pe_ip_all['data']:
		if ('0.0.0.0/0' in s_pia['prefix']) and ('static' in s_pia['protocol']):
			if 'nexthop-addr' in s_pia.keys():
				d_vpn0_interfaces[s_pia['nexthop-ifname']].update({'gateway': s_pia['nexthop-addr']})

# --- ssh to vedge --- #
def activation_test__ssh_vedge(d_conf, s_vedge_ip, d_vpn0_interfaces, d_vpn0_interfaces_down):
	vedge = {
		'device_type': 'cisco_ios',
		'host': s_vedge_ip,
		'username': d_conf['vmanage_username'],
		'password': d_conf['vmanage_password'],
	}

	c_ssh_connection = 0
	net_connect = ''
	try:
		net_connect = ConnectHandler(**vedge)
	except NetMikoAuthenticationException:
		print(' SSH login failed. Please try again.')
		print("\n")
		c_ssh_connection += 1

	except NetMikoTimeoutException:
		print(' vEdge IP address not responding.')
		print("\n")
		c_ssh_connection += 1

	if c_ssh_connection == 0:
		os.system("clear")
		s_start_time = datetime.now()
		s_hostname = net_connect.find_prompt()
		s_hostname = s_hostname.replace("#", "")
		l_test_report = []
		l_test_report.append(2 * '\n')
		l_test_report.append(s_hostname + '\n')
		l_test_report.append(str(s_start_time))
		l_test_report.append(2 * '\n')
		c_tasks = 1


		# ---- process ---- #
		s_cmd = net_connect.send_command('vshell', expect_string='$')
		print('\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': interface mtu / packet size ###\n')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': interface mtu / packet size', '..started')
		print(s_interface_variable)

		c_interface_issue = 0
		for k, v in d_vpn0_interfaces.items():
			if 'gateway' in v.keys():
				if v['color'] in d_conf['mpls_color'] or v['color'] in d_conf['mpls_color']:
					s_src_interface = v['interface'].replace('/', '_')
					s_src_interface = s_src_interface.replace('10ge', 'xge')
					s_cmd = net_connect.send_command('ping %s -c 1 -I %s' % (v['gateway'], s_src_interface))
					s_cmd_re = re.search('1 received', s_cmd)
					if s_cmd_re:
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip_reply': True})
					else:
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip_reply': False})

					s_cmd = net_connect.send_command('ping %s -c 1 -I %s' % (v['gateway'], s_src_interface))
					s_cmd_re = re.search('1 received', s_cmd)
					if s_cmd_re:
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip_reply': True})
					else:
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip_reply': False})

				else:
					s_src_interface = v['interface'].replace('/', '_')
					s_src_interface = s_src_interface.replace('10ge', 'xge')
					s_cmd = net_connect.send_command('ping %s -c 1 -I %s' % (v['gateway'], s_src_interface))
					s_cmd_re = re.search('1 received', s_cmd)
					if s_cmd_re:
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip_reply': True})
					else:
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip': v['gateway']})
						d_vpn0_interfaces[v['interface']].update({'ping_gateway_ip_reply': False})

					s_cmd = net_connect.send_command('ping 8.8.8.8 -c 1 -I %s' % s_src_interface)
					s_cmd_re = re.search('1 received', s_cmd)
					if s_cmd_re:
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip': '8.8.8.8'})
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip_reply': True})
					else:
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip': '8.8.8.8'})
						d_vpn0_interfaces[v['interface']].update({'ping_remote_ip_reply': False})

		if d_vpn0_interfaces_down:
			c_interface_issue += 1
			for v in d_vpn0_interfaces_down.values():
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": down\n")

		for v in d_vpn0_interfaces.values():
			if 'gateway' in v.keys():
				if not v['ping_remote_ip_reply']:
					c_interface_issue += 1
					print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": no connectivity" + Style.RESET_ALL)
					l_test_report.append(v['interface'] + ": no connectivity\n")
				elif v['ping_remote_ip_reply']:
					s_size = 1472
					s_src_interface = v['interface'].replace('/', '_')
					s_src_interface = s_src_interface.replace('10ge', 'xge')
					s_cmd = net_connect.send_command(
						'ping %s -s %s -M do -c 1 -I %s -W 1' % (v['ping_remote_ip'], s_size, s_src_interface))
					s_cmd_re = re.search('1 received', s_cmd)

					c_lower = 0
					while s_cmd_re is None:
						if s_size <= 1460:
							c_lower += 1
							s_size -= 20
							print('           - ' + str(s_size) + '   ', end='\r')
							s_cmd = net_connect.send_command(
							'ping %s -s %s -M do -c 1 -I %s -W 1' % (v['ping_remote_ip'], s_size, s_src_interface))
						elif s_size > 1460:
							s_size -= 1
							print('           - ' + str(s_size) + '   ', end='\r')
							s_cmd = net_connect.send_command(
							'ping %s -s %s -M do -c 1 -I %s -W 1' % (v['ping_remote_ip'], s_size, s_src_interface))
						s_cmd_re = re.search('1 received', s_cmd)

					if c_lower >= 1:
						s_size += 20
						s_cmd = net_connect.send_command(
							'ping %s -s %s -M do -c 1 -I %s -W 1' % (v['ping_remote_ip'], s_size, s_src_interface))
						s_cmd_re = re.search('1 received', s_cmd)

						while s_cmd_re is None:
							s_size -= 1
							print('           - ' + str(s_size) + '   ', end='\r')
							s_cmd = net_connect.send_command(
								'ping %s -s %s -M do -c 1 -I %s -W 1' % (v['ping_remote_ip'], s_size, s_src_interface))
							s_cmd_re = re.search('1 received', s_cmd)

					print('           - ' + v['interface'] + ': ' + str(s_size))
					l_test_report.append(v['interface'] + ': ' + str(s_size) + '\n')

					d_vpn0_interfaces["%s" % v['interface']].update({
						'mtu': s_size
					})
			else:
				c_interface_issue += 1
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": gateway is down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": gateway is down\n")

		if c_interface_issue == 0:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': interface mtu', 'completed')
			print(s_interface_variable)
		else:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': interface mtu', '!!warning')
			print(s_interface_variable)

		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')
		s_cmd = net_connect.send_command('exit', expect_string=r'#')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show version ###\n')
		s_cmd = net_connect.send_command('show version')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show version', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show hardware alarms ###\n')
		s_cmd = net_connect.send_command('show hardware alarms | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show hardware alarms', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show hardware environment ###\n')
		s_cmd = net_connect.send_command('show hardware environment | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show hardware environment', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show hardware inventory ###\n')
		s_cmd = net_connect.send_command('show hardware inventory | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show hardware inventory', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show control connections ###\n')
		s_cmd = net_connect.send_command('show control connections | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show control connections', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show bfd sessions ###\n')
		s_cmd = net_connect.send_command('show bfd sessions | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show bfd sessions', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show bgp summary ###\n')
		s_cmd = net_connect.send_command('show bgp summary | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show bgp summary', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show vrrp ###\n')
		s_cmd = net_connect.send_command('show vrrp | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show vrrp', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show int | tab ###\n')
		s_cmd = net_connect.send_command('show int | tab | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show int | tab', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show interface statistics ###\n')
		s_cmd = net_connect.send_command('show interface statistics | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show interface statistics', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show interface details ###\n')
		s_cmd = net_connect.send_command('show interface detail | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show interface details', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show policy from-vsmart | include from-vsmart ###\n')
		s_cmd = net_connect.send_command('show policy from-vsmart | include from-vsmart | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show policy from-vsmart', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show run vpn 0 ###\n')
		s_cmd = net_connect.send_command('show run vpn 0 | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show run vpn 0', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show run vpn %s ###\n' % d_conf['vpn_id_lan'])
		s_cmd = net_connect.send_command('show run vpn %s | nomore' % d_conf['vpn_id_lan'])
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show run vpn %s' % d_conf['vpn_id_lan'], 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show ip route vpn %s 0.0.0.0/0 ###\n' % d_conf['vpn_id_lan'])
		s_cmd = net_connect.send_command('show ip route vpn 1 0.0.0.0/0 | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show ip route vpn %s 0.0.0.0/0' % d_conf['vpn_id_lan'], 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show ip route vpn %s %s ###\n' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_cmd = net_connect.send_command('show ip route vpn %s %s | nomore' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show ip route vpn %s %s' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']), 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': traceroute vpn %s 8.8.8.8 ###\n' % d_conf['vpn_id_lan'])
		s_cmd = net_connect.send_command('traceroute vpn %s 8.8.8.8 | nomore' % d_conf['vpn_id_lan'])
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': traceroute vpn %s 8.8.8.8' % d_conf['vpn_id_lan'], 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': traceroute vpn %s %s ###\n' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_cmd = net_connect.send_command('traceroute vpn %s %s | nomore' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': traceroute vpn %s %s' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']), 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': ping vpn %s 8.8.8.8 count 10 ###\n' % d_conf['vpn_id_lan'])
		s_cmd = net_connect.send_command('ping vpn %s 8.8.8.8 count 10 | nomore' % d_conf['vpn_id_lan'])
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': ping vpn %s 8.8.8.8' % d_conf['vpn_id_lan'], 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': ping vpn %s %s count 10 ###\n' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_cmd = net_connect.send_command('ping vpn %s %s count 10 | nomore' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']))
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': ping vpn %s %s' % (d_conf['vpn_id_lan'], d_conf['lan_ip_ping']), 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		c_interface_issue = 0
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 gateway', '..started')
		print(s_interface_variable)
		l_test_report.append('### Task ' + str(c_tasks) + ": ping vpn 0 gateway's ###\n")
		l_test_report.append('\n')

		if d_vpn0_interfaces_down:
			c_interface_issue += 1
			for v in d_vpn0_interfaces_down.values():
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": down\n")
				l_test_report.append('\n')

		for v in d_vpn0_interfaces.values():
			if 'gateway' in v.keys():
				if not v['ping_gateway_ip_reply']:
					c_interface_issue += 1
					print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": gateway not responding" + Style.RESET_ALL)
					l_test_report.append(v['interface'] + ": gateway not responding \n")
				elif v['ping_gateway_ip_reply']:
					l_test_report.append('ping vpn 0 %s count 1000 size %s rapid\n' % (v['gateway'], v['mtu']))
					s_cmd = net_connect.send_command(
						'ping vpn 0 %s count 1000 size %s rapid | nomore' % (v['gateway'], v['mtu']))
					print('           - ' + v['interface'] + ': ' + v['gateway'])
					l_test_report.append(s_cmd + '\n')
				l_test_report.append('\n')
			else:
				c_interface_issue += 1
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": gateway is down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": gateway is down \n")
				l_test_report.append('\n')

		if c_interface_issue == 0:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 gateway', 'completed')
			print(s_interface_variable)
		else:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 gateway', '!!warning')
			print(s_interface_variable)

		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		c_interface_issue = 0
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 remote ip', '..started')
		print(s_interface_variable)
		l_test_report.append('### Task ' + str(c_tasks) + ": ping vpn 0 remote ip's ###\n")
		l_test_report.append('\n')

		if d_vpn0_interfaces_down:
			c_interface_issue += 1
			for v in d_vpn0_interfaces_down.values():
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": down\n")
				l_test_report.append('\n')

		for v in d_vpn0_interfaces.values():
			if 'gateway' in v.keys():
				if not v['ping_remote_ip_reply']:
					c_interface_issue += 1
					print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": no connectivity" + Style.RESET_ALL)
					l_test_report.append(v['interface'] + ": no connectivity\n")
					l_test_report.append('\n')
				elif v['ping_remote_ip_reply']:
					l_test_report.append(
						'ping vpn 0 %s count 1000 size %s rapid source %s\n' % (v['ping_remote_ip'], v['mtu'], v['interface']))
					s_cmd = net_connect.send_command(
						'ping vpn 0 %s count 1000 size %s rapid source %s | nomore' % (v['ping_remote_ip'], v['mtu'], v['interface']))
					print('           - ' + v['interface'] + ': ' + v['ping_remote_ip'])
					l_test_report.append(s_cmd + '\n')
				l_test_report.append('\n')
			else:
				c_interface_issue += 1
				print('           - ' + Back.RED + Fore.WHITE + v['interface'] + ": gateway is down" + Style.RESET_ALL)
				l_test_report.append(v['interface'] + ": gateway is down \n")
				l_test_report.append('\n')

		if c_interface_issue == 0:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 remote ip', 'completed')
			print(s_interface_variable)
		else:
			s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', str(c_tasks), ': ping vpn 0 remote ip', '!!warning')
			print(s_interface_variable)

		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		# ---- process ---- #
		c_tasks += 1
		l_test_report.append('### Task ' + str(c_tasks) + ': show interface details ###\n')
		s_cmd = net_connect.send_command(
			'show interface detail | i ge\|loop\|auto\|speed\|dupl\|error\|ali\|col\|ip\|hw\|statu | nomore')
		s_interface_variable = '  {:<4}{:<2}{:<40}{:<10}'.format('Task ', c_tasks, ': show interface details', 'completed')
		print(s_interface_variable)
		l_test_report.append(s_cmd + '\n')
		l_test_report.append('\n')
		l_test_report.append('### Task ' + str(c_tasks) + ': end ###\n')
		l_test_report.append(3 * '\n')

		net_connect.disconnect()
		return s_hostname, l_test_report

# --- send report to email --- #
def activation_test__email(d_conf, s_hostname):
	msg = MIMEMultipart()
	msg['Subject'] = 'vEdge activation test results for %s' % s_hostname
	msg['From'] = 'viptela_automation@cz.verizon.com'
	msg['To'] = d_conf['my_email']

	body = "vEdge activation successfully tested. Result are stored in attachment."

	msg.attach(MIMEText(body, 'plain'))

	filename = 'activation_test_%s.txt' % s_hostname
	attachment = open(d_conf['userpath'] + '/viptela/completed/' + filename, "rb")
	p = MIMEBase('application', 'octet-stream')
	p.set_payload((attachment).read())
	p.add_header('Content-Disposition', "attachment; filename=%s" % filename)
	msg.attach(p)

	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()

# --- save report to file --- #
def activation_test__tracker(d_conf, s_hostname, l_test_report, l_speed_test_results):
	s_folder = os.path.isdir(d_conf['userpath'] + '/viptela/completed')
	if not s_folder:
		os.mkdir(d_conf['userpath'] + '/viptela/completed')
		os.chmod(d_conf['userpath'] + '/viptela/completed', 0o700)

	f = open(d_conf['userpath']+'/viptela/completed/activation_test_%s.txt' % s_hostname, 'w')
	for s_tr in l_test_report:
		f.write(s_tr)

	for s_str in l_speed_test_results:
		f.write(s_str + '\n')

	f.close()
	os.chmod(d_conf['userpath']+'/viptela/completed/activation_test_%s.txt' % s_hostname,
	         0o600)

# --- ip address validation --- #
def ip_validation(ip_address):
	s_ip_address = ip_address.strip()
	while True:
		try:
			s_ip = ipaddress.ip_address(s_ip_address)
		except ValueError:
			print("  ! IP has incorrect format !\n")
			print("  => ", end="")
			s_ip_address = input()
			s_ip_address = s_ip_address.strip()
		else:
			break
	return s_ip_address

# --- main menu --- #
os.system("clear")
if __name__ == "__main__":
	gs_session, gd_conf = authentication.login()
	print('\n')
	gs_vedge_ip_i = input('  vEdge ip: ')
	gs_vedge_ip = ip_validation(gs_vedge_ip_i)
	print('\n')
	os.system("clear")
	print('\n')
	print('  vEdge connectivity test service started:\n')
	gs_vedge_sn, gs_vedge_name, gs_vedge_reachable = activation_test__source_vedge(gs_session, gd_conf, gs_vedge_ip)
	print('  - vEdge info:         done')
	if not 'unreachable' in gs_vedge_reachable:
		gd_vpn0_interfaces, gd_vpn0_interfaces_down = activation_test__interfaces(gs_session, gd_conf, gs_vedge_ip)
		print('  - interfaces:         done')
		activation_test__interface_color(gs_session, gd_conf, gs_vedge_ip, gd_vpn0_interfaces)
		print('  - colors:             done')
		activation_test__pe_ip(gs_session, gd_conf, gs_vedge_ip, gd_vpn0_interfaces)
		print('  - default gateway:    done')
		gs_hostname, gl_test_report = activation_test__ssh_vedge(gd_conf, gs_vedge_ip, gd_vpn0_interfaces, gd_vpn0_interfaces_down)

		# --- speed test --- #
		gl_speed_test_results = []
		if not 'unreachable' in gs_vedge_reachable:
			gd_gateway_interface = speed_test__pe_ip(gs_session, gd_conf, gs_vedge_ip)
			gs_vedge_color = speed_test__colors(gs_session, gd_conf, gs_vedge_ip, gd_gateway_interface)
			gl_destination_vedge_ips = speed_test__bfd_sessions(gs_session, gd_conf, gs_vedge_ip, gs_vedge_color)
			gs_destination_vedge_name, gs_destination_vedge_sn, gs_destination_vedge_ip, gs_destination_vedge_reachable = speed_test__destination_vedge(
				gs_session, gd_conf, gl_destination_vedge_ips)

			if not 'unreachable' in gs_vedge_reachable and not 'unreachable' in gs_destination_vedge_reachable:
				gs_speed_session_id = speed_test__parameters(gs_session, gd_conf, gs_vedge_ip, gs_vedge_sn,
				                                             gs_destination_vedge_ip, gs_vedge_color)
				gs_speedtest_status_fail = speed_test__start(gs_session, gd_conf, gs_speed_session_id)
				if not gs_speedtest_status_fail:
					gc_speedtest = speed_test__live_results(gs_session, gd_conf, gs_speed_session_id, gs_vedge_ip)
					if gc_speedtest > 25:
						speed_test__history_results(gs_session, gd_conf, gs_vedge_ip, gs_speed_session_id)
				else:
					speed_test__history_results(gs_session, gd_conf, gs_vedge_ip, gs_speed_session_id)
				speed_test__stop(gs_session, gd_conf, gs_speed_session_id)
				gl_speed_test_results = speed_test__tracker()
			else:
				print("\n")
				print("  Destination vEdge is unreachable in vManage")
				print("\n")

		else:
			print("\n")
			print("  Source vEdge is unreachable in vManage")
			print("\n")

		activation_test__tracker(gd_conf, gs_hostname, gl_test_report, gl_speed_test_results)
		activation_test__email(gd_conf, gs_hostname)

	else:
		print("\n")
		print("  vEdge is unreachable in vManage")
		print("\n")


