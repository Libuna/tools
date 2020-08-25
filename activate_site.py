#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import authentication
import getpass
from template_attach import *
from template_detach import *
from image_upgrade import *
from image_default import *
from activation_test import *
from smart_account_add_serial_number import *
from smart_account_verify_serial_number import *
from smart_account_sync_vmanage_with_cisco import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- vEdge info  --- #
def activate_site__vedge_info(s_session, d_conf):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/system/device/vedges'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vedge_info_all_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vedge_info_all_error_message, indent=2, sort_keys=True))
		exit()
	d_vedge_info_all = json.loads(r.content.decode('utf8'))

	s_vedge_model = ''
	s_vedge_uuid = ''
	s_vedge_hostname = ''
	s_vedge_ip = ''
	s_vedge_image_version = ''
	s_vedge_image_default = ''
	s_vedge_template = ''
	s_vedge_rechable = ''
	s_vedge_config = ''
	for s_via in d_vedge_info_all['data']:
		s_via_re = re.search('^' + gs_vedge_sn + '$', s_via['uuid'])
		if s_via_re:
			if 'deviceModel' in s_via.keys():
				s_vedge_model = s_via['deviceModel']
			if 'uuid' in s_via.keys():
				s_vedge_uuid = s_via['uuid']
			if 'host-name' in s_via.keys():
				s_vedge_hostname = s_via['host-name']
			if 'system-ip' in s_via.keys():
				s_vedge_ip = s_via['system-ip']
			if 'version' in s_via.keys():
				s_vedge_image_version = s_via['version']
			if 'defaultVersion' in s_via.keys():
				s_vedge_image_default = s_via['defaultVersion']
			if 'template' in s_via.keys():
				s_vedge_template = s_via['template']
			if 'reachability' in s_via.keys():
				s_vedge_rechable = s_via['reachability']
			if 'configStatusMessage' in s_via.keys():
				s_vedge_config = s_via['configStatusMessage']

	# ---- LAN service ports ---- #
	d_vedge_service_ports = {}
	if s_vedge_ip and not 'unreachable' in s_vedge_rechable:
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/interface?deviceId=%s&&&' % s_vedge_ip
		r = gs_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vedge_service_ports_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vedge_service_ports_error_message, indent=2, sort_keys=True))
			exit()
		d_vedge_service_ports_all = json.loads(r.content.decode('utf8'))

		for s_vi in d_vedge_service_ports_all['data']:
			if 'ifname' in s_vi.keys() and 'af-type' in s_vi.keys() and 'port-type' in s_vi.keys() and 'ip-address' in s_vi.keys():
				s_vi_re = re.search('ge\d+/\d+|10ge\d+/\d+|ppp\d+', s_vi['ifname'])
				if s_vi_re and 'ipv4' in s_vi['af-type'] and 'service' in s_vi['port-type'] and not '-' in s_vi['ip-address']:
					d_vedge_service_ports[s_vi['ifname']] = ({'ifname':s_vi['ifname']})
					d_vedge_service_ports[s_vi['ifname']].update({'if-oper-status':s_vi['if-oper-status']})
					d_vedge_service_ports[s_vi['ifname']].update({'if-admin-status':s_vi['if-admin-status']})

				if s_vi_re and 'ipv4' in s_vi['af-type'] and 'Up' in s_vi['if-admin-status'] and 'Up' in s_vi[
					'if-oper-status'] and 'service' in s_vi['port-type'] and not '-' in s_vi['ip-address']:
					d_vedge_service_ports[s_vi['ifname']].update({'port_status': '    ok'})
				elif s_vi_re and 'ipv4' in s_vi['af-type'] and 'Up' in s_vi['if-admin-status'] and 'Down' in s_vi[
					'if-oper-status'] and 'service' in s_vi['port-type'] and not '-' in s_vi['ip-address']:
					d_vedge_service_ports[s_vi['ifname']].update({'port_status': 'NOT ok'})
				elif s_vi_re and 'ipv4' in s_vi['af-type'] and 'Down' in s_vi['if-admin-status'] and 'Down' in s_vi[
					'if-oper-status'] and 'service' in s_vi['port-type'] and not '-' in s_vi['ip-address']:
					d_vedge_service_ports[s_vi['ifname']].update({'port_status': 'NOT ok'})

	# --- vEdge status (ok/not ok, presence/missing) --- #
	if not s_vedge_uuid:
		s_vedge_uuid_status = 'NOT ok'
	else:
		s_vedge_uuid_status = '    ok'

	if not s_vedge_model:
		s_vedge_model_status = 'NOT ok'
	else:
		s_vedge_model_status = '    ok'

	if not s_vedge_hostname:
		s_vedge_hostname_status = 'NOT ok'
	else:
		s_vedge_hostname_status = '    ok'

	if not s_vedge_ip:
		s_vedge_ip_status = 'NOT ok'
	else:
		s_vedge_ip_status = '    ok'

	if not s_vedge_image_version:
		s_vedge_image_version_status = 'NOT ok'
	elif d_conf['vedge_image_version'] != s_vedge_image_version:
		s_vedge_image_version_status = '  warn'
	else:
		s_vedge_image_version_status = '    ok'

	if not s_vedge_image_default:
		s_vedge_image_default_status = 'NOT ok'
	elif d_conf['vedge_image_version'] != s_vedge_image_default:
		s_vedge_image_default_status = '  warn'
	else:
		s_vedge_image_default_status = '    ok'

	if not s_vedge_template:
		s_vedge_template_status = 'NOT ok'
	else:
		s_vedge_template_status = '    ok'

	s_vedge_rechable_re = re.search('^-$|^unreachable', s_vedge_rechable)
	if not s_vedge_rechable:
		s_vedge_rechable_status = 'NOT ok'
	elif s_vedge_rechable_re:
		s_vedge_rechable_status = 'NOT ok'
	else:
		s_vedge_rechable_status = '    ok'

	s_vedge_config_status_re = re.search('^-$|Sync Pending|Out of Sync', s_vedge_config)
	if not s_vedge_config:
		s_vedge_config_status = 'NOT ok'
	elif s_vedge_config_status_re:
		s_vedge_config_status = 'NOT ok'
	else:
		s_vedge_config_status = '    ok'

	s_activation_status = ''
	if not s_vedge_uuid and not s_vedge_model:
		s_activation_status = 'SN is not registered in vManage'
	elif not 'NOT ok' in s_vedge_uuid_status and not 'NOT ok' in s_vedge_model_status and not 'NOT ok' in s_vedge_model_status and not 'NOT ok' in s_vedge_hostname_status and not 'NOT ok' in s_vedge_ip_status and not 'NOT ok' in s_vedge_image_version_status and not 'NOT ok' in s_vedge_image_default_status and not 'NOT ok' in s_vedge_template_status and not 'NOT ok' in s_vedge_rechable_status and not 'NOT ok' in s_vedge_config_status:
		c_service_port_status = 0
		if d_vedge_service_ports:
			for k, v in d_vedge_service_ports.items():
				if 'NOT ok' in v['port_status']:
					c_service_port_status += 1
		if c_service_port_status == 0:
			s_activation_status = 'activated'
		else:
			s_activation_status = 'not activated'
	else:
		s_activation_status = 'not activated'

	return s_vedge_model, s_vedge_uuid, s_vedge_hostname, s_vedge_ip, s_vedge_image_version, s_vedge_image_default, \
	       s_vedge_template, s_vedge_rechable, s_vedge_config, \
	       s_vedge_model_status, s_vedge_uuid_status, s_vedge_hostname_status, s_vedge_ip_status, s_vedge_image_version_status, \
	       s_vedge_image_default_status, s_vedge_template_status, s_vedge_rechable_status, s_vedge_config_status, d_vedge_service_ports, \
	       s_activation_status


## ----- Print vEdge ino ----- ##
def activate_site__print_vedge_info(s_vedge_model, s_vedge_uuid, s_vedge_hostname, s_vedge_ip, s_vedge_image_version,
s_vedge_image_default, s_vedge_template, s_vedge_rechable, s_vedge_config, s_vedge_model_status, s_vedge_uuid_status,
s_vedge_hostname_status, s_vedge_ip_status, s_vedge_image_version_status, s_vedge_image_default_status,
s_vedge_template_status, s_vedge_rechable_status, s_vedge_config_status, d_vedge_service_ports, s_activation_status):
	print('''

  =======================================================================================================>>>
  +                                          vEdge site activation                                         +
  + lipa-devops                                                                                     v.1.1  +
  =======================================================================================================>>>
	''')

	l_right_tab = ['| 1.  Refresh menu', '| 2.  Attach template', '| 3.  Detach template', '| 4.  Image upgrade',
	               '| 5.  Image default', '| 6.  Activation tests', '| 7.  Speed test', '| 8.  Change serial number',
	               '| 9.  Exit']

	l_left_tab = []
	print('  vEdge activation STATUS: ', s_activation_status)
	print(' ')
	s_menu = '  {:<75}{:<10}'.format(' ', '  Main Menu:')
	print(s_menu)
	s_vedge_model_report = '  {:<21}{:<9}{:<44}'.format('model:', s_vedge_model_status, s_vedge_model)
	l_left_tab.append(s_vedge_model_report)

	c_vedge_sn = len(gs_vedge_uuid)
	if c_vedge_sn > 40:
		s_vedge_uuid_report = '  {:<21}{:<9}{:<44}'.format('serial number:', s_vedge_uuid_status,
		                                                   s_vedge_uuid[:40] + '$..')
	else:
		s_vedge_uuid_report = '  {:<21}{:<9}{:<44}'.format('serial number:', s_vedge_uuid_status, s_vedge_uuid)
	l_left_tab.append(s_vedge_uuid_report)

	s_vedge_hostname_report = '  {:<21}{:<9}{:<44}'.format('hostname:', s_vedge_hostname_status, s_vedge_hostname)
	l_left_tab.append(s_vedge_hostname_report)

	s_vedge_ip_report = '  {:<21}{:<9}{:<44}'.format('system-ip:', s_vedge_ip_status, s_vedge_ip)
	l_left_tab.append(s_vedge_ip_report)

	s_vedge_image_version_report = '  {:<21}{:<9}{:<44}'.format('image version:', s_vedge_image_version_status, s_vedge_image_version)
	l_left_tab.append(s_vedge_image_version_report)

	s_vedge_default_report = '  {:<21}{:<9}{:<44}'.format('image default:', s_vedge_image_default_status,
	                                                      s_vedge_image_default)
	l_left_tab.append(s_vedge_default_report)

	s_vedge_reachibility_report = '  {:<21}{:<9}{:<44}'.format('reachability:', s_vedge_rechable_status,
	                                                           s_vedge_rechable)
	l_left_tab.append(s_vedge_reachibility_report)

	s_vedge_config_report = '  {:<21}{:<9}{:<44}'.format('config status:', s_vedge_config_status,
	                                                     s_vedge_config)
	l_left_tab.append(s_vedge_config_report)

	c_vedge_template = len(gs_vedge_template)
	if c_vedge_template > 40:
		s_vedge_template_report = '  {:<21}{:<9}{:<44}'.format('template:', s_vedge_template_status,
		                                                       s_vedge_template[:40] + '$..')
	else:
		s_vedge_template_report = '  {:<21}{:<9}{:<44}'.format('template:', s_vedge_template_status, s_vedge_template)
	l_left_tab.append(s_vedge_template_report)

	if d_vedge_service_ports:
		for k, v in d_vedge_service_ports.items():

			s_vedge_service_port_report = '  {:<21}{:<9}{:<11}{:<6}{:<38}'.format('service port:',v['port_status'],
			                                                         v['ifname'], v['if-admin-status'], v['if-oper-status'])
			l_left_tab.append(s_vedge_service_port_report)

	for x, y in itertools.zip_longest(l_left_tab, l_right_tab):
		if y is None:
			print(x)
		elif x is None:
			y = '  {:<75}{:<10}'.format(' ', y)
			print(y)
		else:
			print(x, y)

	print(
		'  ------------------------------------------------------------------------------------------------------->>>')


## --- Menu --- ##
def activate_site__menu_options():
	print('''  ------------------------------------------------------------------------------------------------------->>>

  >> Choose option: <<
  =>: ''', end='')


## ---------- tracker ------------- ##
def activate_site__tracker(s_vedge_hostname, s_vedge_sn):
	username = getpass.getuser()
	date = str(datetime.now())

	fr = open('/home/repos/public/konecranes/viptela/tracker_vedge_site_activation.csv', 'r')
	l_tracker = fr.readlines()
	fr.close()

	l_u_tracker = []
	for lt in l_tracker:
		l_u_tracker.append(lt)

	l_u_tracker.append(username + ',' + date + ',' + gs_vedge_hostname + ',' + gs_vedge_sn + '\n')

	fw = open('/home/repos/public/konecranes/viptela/tracker_vedge_site_activation.csv', 'w')

	for lut in l_u_tracker:
		fw.write(lut)
	fw.close()


# --- main menu --- #
os.system("clear")
try:
	gs_vedge_sn = sys.argv[1]
	gs_vedge_sn = gs_vedge_sn.strip()
	gs_vedge_sn_re = re.search('\w', gs_vedge_sn)
except:
	print("\n")
	gs_vedge_sn = input('  Serial number: ')
	gs_vedge_sn = gs_vedge_sn.strip()
	gs_vedge_sn_re = re.search('\w', gs_vedge_sn)
	os.system("clear")
while gs_vedge_sn_re is None:
	print('\n')
	print("  ! SN has incorrect format !\n")
	gs_vedge_sn = input('  Serial number: ')
	gs_vedge_sn = gs_vedge_sn.strip()
	gs_vedge_sn_re = re.search('\w', gs_vedge_sn)

os.system("clear")
gs_session, gd_conf = authentication.login()

gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default,
gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status,
gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status,
gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, gs_activation_status)
activate_site__menu_options()
# activate_site__tracker(gs_vedge_hostname, gs_vedge_sn)

if 'SN is not registered in vManage' in gs_activation_status:
	cisco_sava_message = ''
	gs_cisco_add_description = ''
	gs_cisco_access_token, gs_cisco_sn_status = smart_account_verify_serial_number__verification(gd_conf, gs_vedge_sn)
	if gs_cisco_sn_status:
		smart_account_sync_vmanage_with_cisco__sync_smart_account(gs_session, gd_conf)
	else:
		gs_cisco_add_status, gs_cisco_add_message, gs_cisco_add_validation, gs_cisco_add_description = smart_account_add_serial_number__add_serial(
			gd_conf, gs_vedge_sn)

		if 'FAILED' in gs_cisco_add_message:
			print('\n')
			print('  status       ', gs_cisco_add_status)
			print('  message:     ', gs_cisco_add_message)
			print('  validation:  ', gs_cisco_add_validation)
			print('  description: ', gs_cisco_add_description)
			print('\n')
		else:
			smart_account_sync_vmanage_with_cisco__sync_smart_account(gs_session, gd_conf)
			cisco_sava_message = 'SN has been added to VA account.'

	gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
	gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
	gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
	gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
	gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)

	if gs_cisco_add_description:
		if 'Device already claimed' in gs_cisco_add_description:
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !!', gs_cisco_add_description)
			print('  !! Please raise a TAC ticket to move SN into correct VA account.')
		else:
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !!', gs_cisco_add_description)
	if cisco_sava_message:
		activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
		                                gs_vedge_image_version, gs_vedge_image_default,
		                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status,
		                                gs_vedge_uuid_status, gs_vedge_hostname_status,
		                                gs_vedge_ip_status, gs_vedge_image_version_status,
		                                gs_vedge_image_default_status, gs_vedge_template_status,
		                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
		                                gs_activation_status)
		print('  !! STATUS MESSAGE:')
		print('  !!', cisco_sava_message)
	activate_site__menu_options()

c_menu = 0
while c_menu < 1:
	s_menu_option = ''
	i, o, e = select.select([sys.stdin], [], [], 600)
	if (i):
		s_menu_option = sys.stdin.readline()
	else:
		print('')
		print('  Timeout ...')
		print('')
		exit()
	s_menu_option = s_menu_option.strip()
	s_menu_option_re = re.search('^([1-9]|exit)$', s_menu_option)
	while s_menu_option_re is None:
		print('''
  >> Choose option: <<
  =>: ''', end='')
		i, o, e = select.select([sys.stdin], [], [], 600)
		if (i):
			s_menu_option = sys.stdin.readline()
		else:
			print('')
			print('  Timeout ...')
			print('')
			exit()
		s_menu_option = s_menu_option.strip()
		s_menu_option_re = re.search('^([1-9])$|exit', s_menu_option)

	# --- exit menu --- #
	if '9' in s_menu_option:
		c_menu += 1
		print('\n')

	elif '8' in s_menu_option:
		os.system("clear")
		print("\n")
		gs_vedge_sn = input('  Serial number: ')
		gs_vedge_sn = gs_vedge_sn.strip()
		gs_vedge_sn_re = re.search('\w', gs_vedge_sn)
		os.system("clear")
		while gs_vedge_sn_re is None:
			print('\n')
			print("  ! SN has incorrect format !\n")
			gs_vedge_sn = input('   - Serial number: ')
			gs_vedge_sn = gs_vedge_sn.strip()
			gs_vedge_sn_re = re.search('\w', gs_vedge_sn)

		gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
		gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
		gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
		gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
		gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
		activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
		                                gs_vedge_image_version, gs_vedge_image_default,
		                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
		                                gs_vedge_model_status,
		                                gs_vedge_uuid_status, gs_vedge_hostname_status,
		                                gs_vedge_ip_status, gs_vedge_image_version_status,
		                                gs_vedge_image_default_status, gs_vedge_template_status,
		                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
		                                gs_activation_status)
		activate_site__menu_options()

		if 'SN is not registered in vManage' in gs_activation_status:
			cisco_sava_message = ''
			gs_cisco_add_description = ''
			gs_cisco_access_token, gs_cisco_sn_status = smart_account_verify_serial_number__verification(gd_conf,
			                                                                                             gs_vedge_sn)
			if gs_cisco_sn_status:
				smart_account_sync_vmanage_with_cisco__sync_smart_account(gs_session, gd_conf)
			else:
				gs_cisco_add_status, gs_cisco_add_message, gs_cisco_add_validation, gs_cisco_add_description = smart_account_add_serial_number__add_serial(
					gd_conf, gs_vedge_sn)

				if 'FAILED' in gs_cisco_add_message:
					print('\n')
					print('  status       ', gs_cisco_add_status)
					print('  message:     ', gs_cisco_add_message)
					print('  validation:  ', gs_cisco_add_validation)
					print('  description: ', gs_cisco_add_description)
					print('\n')
				else:
					smart_account_sync_vmanage_with_cisco__sync_smart_account(gs_session, gd_conf)
					cisco_sava_message = 'SN has been added to VA account.'

			gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
			gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
			gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
			gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
			gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)

			if gs_cisco_add_description:
				if 'Device already claimed' in gs_cisco_add_description:
					activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
					                                gs_vedge_image_version, gs_vedge_image_default,
					                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
					                                gs_vedge_model_status, gs_vedge_uuid_status,
					                                gs_vedge_hostname_status,
					                                gs_vedge_ip_status, gs_vedge_image_version_status,
					                                gs_vedge_image_default_status, gs_vedge_template_status,
					                                gs_vedge_reachable_status, gs_vedge_config_status,
					                                gd_vedge_service_ports,
					                                gs_activation_status)
					print('  !! STATUS MESSAGE:')
					print('  !!', gs_cisco_add_description)
					print('  !! Please raise a TAC ticket to move SN into correct VA account.')
				else:
					activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
					                                gs_vedge_image_version, gs_vedge_image_default,
					                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
					                                gs_vedge_model_status, gs_vedge_uuid_status,
					                                gs_vedge_hostname_status,
					                                gs_vedge_ip_status, gs_vedge_image_version_status,
					                                gs_vedge_image_default_status, gs_vedge_template_status,
					                                gs_vedge_reachable_status, gs_vedge_config_status,
					                                gd_vedge_service_ports,
					                                gs_activation_status)
					print('  !! STATUS MESSAGE:')
					print('  !!', gs_cisco_add_description)

	# --- speed test --- #
	elif '7' in s_menu_option:
		if 'unreachable' in gs_vedge_reachable or 'In Sync' not in gs_vedge_config:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge must be reachable and synchronized.')
			activate_site__menu_options()
		else:
			os.system("clear")
			s_speed_test_message = ''
			gl_speed_test_results = []
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
				os.system("clear")
				print("\n")
				print("  Destination vEdge is unreachable in vManage.")
				s_speed_test_message = '  !! Destination vEdge is unreachable in vManage.'
				print("\n")

			os.system("clear")
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			if s_speed_test_message:
				print(s_speed_test_message)
			else:
				for s_str in gl_speed_test_results:
					if 'speed-down:' in s_str:
						print('  ++ ' + s_str.lstrip())
					if 'speed-up:' in s_str:
						print('  ++ ' + s_str.lstrip())
					if 'dst-ip:' in s_str:
						print('  ++ ' + s_str.lstrip())
					if 'speed test did not finish in time' in s_str:
						print('  ++ ' + s_str.lstrip())
			activate_site__menu_options()

	# --- activation test --- #
	elif '6' in s_menu_option:
		if 'unreachable' in gs_vedge_reachable or 'In Sync' not in gs_vedge_config:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge must be reachable and synchronized.')
			activate_site__menu_options()
		else:
			os.system("clear")
			gd_vpn0_interfaces, gd_vpn0_interfaces_down = activation_test__interfaces(gs_session, gd_conf, gs_vedge_ip)
			activation_test__interface_color(gs_session, gd_conf, gs_vedge_ip, gd_vpn0_interfaces)
			activation_test__pe_ip(gs_session, gd_conf, gs_vedge_ip, gd_vpn0_interfaces)
			gs_hostname, gl_test_report = activation_test__ssh_vedge(gd_conf, gs_vedge_ip, gd_vpn0_interfaces,
			                                                         gd_vpn0_interfaces_down)

			# --- speed test --- #
			gl_speed_test_results = []
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

				activation_test__tracker(gd_conf, gs_hostname, gl_test_report, gl_speed_test_results)
				activation_test__email(gd_conf, gs_hostname)
				s_activation_test_message = '  !! Activation test results were sent to your mailbox.'
			else:
				os.system("clear")
				print("\n")
				print("  Destination vEdge is unreachable in vManage.")
				s_activation_test_message = '  !! Destination vEdge is unreachable in vManage.'
				print("\n")

			os.system("clear")
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print(s_activation_test_message)
			activate_site__menu_options()

	# --- image default --- #
	elif '5' in s_menu_option:
		if not gs_vedge_model or not gs_vedge_uuid:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge SN is not yet registered with vManage.')
			activate_site__menu_options()
		elif not gs_vedge_reachable or 'unreachable' in gs_vedge_reachable:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge is not reachable from vManage.')
			activate_site__menu_options()
		elif gd_conf['vedge_image_version'] == gs_vedge_image_default:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  => vEdge default image is installed.')
			activate_site__menu_options()
		elif gd_conf['vedge_image_version'] != gs_vedge_image_version:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! Upgrade vEdge before setting default partition.')
			activate_site__menu_options()
		else:
			gs_image_default_status = image_default__default_partition(gs_session, gd_conf, gs_vedge_sn, gs_vedge_ip)
			os.system("clear")
			gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
			gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
			gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
			gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
			gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE !!')
			print('  ++ vEdge default partition status: ', gs_image_default_status)
			activate_site__menu_options()

	# --- image upgrade --- #
	elif '4' in s_menu_option:
		if not gs_vedge_model or not gs_vedge_uuid:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge SN is not yet registered with vManage')
			activate_site__menu_options()
		elif not gs_vedge_reachable or 'unreachable' in gs_vedge_reachable:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge is not reachable from vManage')
			activate_site__menu_options()
		elif gd_conf['vedge_image_version'] == gs_vedge_image_version:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  => vEdge has the standard image version.')
			activate_site__menu_options()
		else:
			gs_image_upgrade_status = image_upgrade__image_upgrade(gs_session, gd_conf, gs_vedge_sn, gs_vedge_ip)
			os.system("clear")
			gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
			gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
			gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
			gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
			gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  ++ vEdge image installation status: ', gs_image_upgrade_status)
			activate_site__menu_options()

	# --- detach template --- #
	elif '3' in s_menu_option:
		if not gs_vedge_template:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge does not have attached template.')
			activate_site__menu_options()
		else:
			gs_template_detach_status = template_detach__detach_template(gs_session, gd_conf, gs_vedge_sn, gs_vedge_ip)

			gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
			gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
			gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
			gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
			gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  -- Template detach status: ' + gs_template_detach_status)
			activate_site__menu_options()

	# --- attach template --- #
	elif '2' in s_menu_option:
		if not gs_vedge_model or not gs_vedge_uuid:
			os.system("clear")
			time.sleep(1)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  !! vEdge SN is not yet registered with vManage.')
			activate_site__menu_options()
		else:
			gs_template_attach_status = ''
			gl_vedge_template, gs_vedge_template_id = template_attach__template_list(gs_session, gd_conf)
			gd_template_form_updated = template_attach__update_template(gs_session, gd_conf, gs_vedge_sn,
			                                                            gs_vedge_template_id)
			if gd_template_form_updated:
				gs_template_attach_status = template_attach__attach_template(gs_session, gd_conf, gd_template_form_updated)

			gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
			gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
			gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
			gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
			gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
			activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
			                                gs_vedge_image_version, gs_vedge_image_default,
			                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config,
			                                gs_vedge_model_status,
			                                gs_vedge_uuid_status, gs_vedge_hostname_status,
			                                gs_vedge_ip_status, gs_vedge_image_version_status,
			                                gs_vedge_image_default_status, gs_vedge_template_status,
			                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
			                                gs_activation_status)
			print('  !! STATUS MESSAGE:')
			print('  ++ Template attach status: ' + gs_template_attach_status)
			activate_site__menu_options()

	# --- refresh menu --- #
	elif '1' in s_menu_option:
		os.system("clear")
		gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip, gs_vedge_image_version, gs_vedge_image_default, \
		gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status, gs_vedge_uuid_status, gs_vedge_hostname_status, \
		gs_vedge_ip_status, gs_vedge_image_version_status, gs_vedge_image_default_status, gs_vedge_template_status, \
		gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports, \
		gs_activation_status = activate_site__vedge_info(gs_session, gd_conf)
		activate_site__print_vedge_info(gs_vedge_model, gs_vedge_uuid, gs_vedge_hostname, gs_vedge_ip,
		                                gs_vedge_image_version, gs_vedge_image_default,
		                                gs_vedge_template, gs_vedge_reachable, gs_vedge_config, gs_vedge_model_status,
		                                gs_vedge_uuid_status, gs_vedge_hostname_status,
		                                gs_vedge_ip_status, gs_vedge_image_version_status,
		                                gs_vedge_image_default_status, gs_vedge_template_status,
		                                gs_vedge_reachable_status, gs_vedge_config_status, gd_vedge_service_ports,
		                                gs_activation_status)
		activate_site__menu_options()
