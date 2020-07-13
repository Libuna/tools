#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                   #
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

# --- data prefix list, choose prefix list name and get list name unique id --- #
def prefix_lists_and_prefix_list_id(s_session, d_conf):
	os.system("clear")
	print(2 * "\n")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/policy/list/dataprefix/'
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_prefix_lists_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_prefix_lists_error_message, indent=2, sort_keys=True))
		exit()
	d_prefix_lists = json.loads(r.content.decode('utf8'))
	l_prefix_lists = []
	d_prefix_list_id = {}
	for s_pl in d_prefix_lists['data']:
		l_prefix_lists.append(s_pl['name'])
		d_prefix_list_id[s_pl['name']] = s_pl['listId']

	l_prefix_lists.sort()
	print("  Data prefix list names:\n")

	c_prefix_lists = (len(l_prefix_lists))
	c1 = int(c_prefix_lists / 3)
	c2 = 3 * int(c1)
	if c2 < c_prefix_lists:
		c1 = int(c1 + 1)

	a = (l_prefix_lists[:c1])
	b = (l_prefix_lists[c1:c1 + c1])
	c = (l_prefix_lists[c1 + c1:])

	for x, y, z in itertools.zip_longest(a, b, c):
		if x and y and z:
			s_prefix_lists = '  {:<42}{:<42}{:<42}'.format(x, y, z)
			print(s_prefix_lists)
		elif x and y:
			s_prefix_lists = '  {:<42}{:<42}'.format(x, y)
			print(s_prefix_lists)
		else:
			s_prefix_lists = '  {:<42}'.format(x)
			print(s_prefix_lists)

	print("\n")
	print("  >> Type a data prefix list name to see list of prefixes: <<")
	print("  => ", end="")
	s_prefix_list_name_i = input()
	s_prefix_list_name_i = s_prefix_list_name_i.strip()
	n = 0
	for s_pl in l_prefix_lists:
		s_pl = s_pl.strip()
		s_pl_re = re.search('^' + re.escape(s_prefix_list_name_i) + '$', s_pl)
		if s_pl_re is not None:
			n = n + 1
			# print(s_prefix_list_name_i)
			# print(d_prefix_list_id.get('%s'%s_prefix_list_name_i))
	#
	while n is 0:
		print("  !! Data prefix list name doesn't match. Type again: !!")
		print("  => ", end="")
		s_prefix_list_name_i = input()
		s_prefix_list_name_i = s_prefix_list_name_i.strip()
		for s_pl in l_prefix_lists:
			s_pl = s_pl.strip()
			s_pl_re = re.search('^' + re.escape(s_prefix_list_name_i) + '$', s_pl)
			if s_pl_re is not None:
				n = n + 1
				# print(s_prefix_list_name_i)
				# print(d_prefix_list_id.get('%s' % s_prefix_list_name_i))
	return (d_prefix_list_id.get('%s' % s_prefix_list_name_i),s_prefix_list_name_i)

# --- data prefix list id, see all prefixes inside list --- #
def prefixes_in_list(s_session, d_conf):
	os.system("clear")
	print("\n")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/policy/list/dataprefix/' + gl_prefix_list_id
	r = s_session.get(url=url, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	print("\n")
	if '200' not in r.status_code:
		print("  HTTP Status Code - " + r.status_code)
		d_prefixes_in_list_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_prefixes_in_list_error_message, indent=2, sort_keys=True))
		exit()
	d_prefixes_in_list_present = json.loads(r.content.decode('utf8'))
	d_prefixes_in_list_toupdate = json.loads(r.content.decode('utf8'))
	l_prefixes_in_list = []
	# l_prefixes_in_list.append('\n')
	l_prefixes_in_list.append('  Prefixes from: ' + gl_prefix_list_name)
	l_prefixes_in_list.append('\n')
	for s_pilp in d_prefixes_in_list_present['entries']:
		l_prefixes_in_list.append(s_pilp['ipPrefix'])
	os.system("clear")
	print("\n")
	for s_pil in l_prefixes_in_list:
		s_pil = s_pil.strip()
		print('  ' + s_pil)
	d_prefixes_in_list_toupdate.pop('lastUpdated', None)
	d_prefixes_in_list_toupdate.pop('owner', None)
	d_prefixes_in_list_toupdate.pop('readOnly', None)
	d_prefixes_in_list_toupdate.pop('version', None)
	d_prefixes_in_list_toupdate.pop('referenceCount', None)
	d_prefixes_in_list_toupdate.pop('isActivatedByVsmart', None)
	return (d_prefixes_in_list_present,d_prefixes_in_list_toupdate)

# --- add/remove prefix from list - yes or no --- #
def prefixes_add_remove_yn(prefix_add_remove,prefix_from_to):
	print("\n")
	print("  >> %s prefix? (y/n): <<" % prefix_add_remove)
	print("  => ", end="")
	s_prefixes_add_remove_yn_i = input()
	s_prefixes_add_remove_yn_re = re.search('[y|n]', s_prefixes_add_remove_yn_i)
	while s_prefixes_add_remove_yn_re is None:
		print("  !! Select from above options. Please try again: !!")
		print("  => ", end="")
		s_prefixes_add_remove_yn_i = input()
		if s_prefixes_add_remove_yn_i is "y":
			return
		if s_prefixes_add_remove_yn_i is "n":
			exit()
	if s_prefixes_add_remove_yn_i is "y":
		return
	if s_prefixes_add_remove_yn_i is "n":
		exit()

# --- add/remove prefix from list --- #
def prefixes_add_remove(prefix_add_remove,prefix_from_to,append_remove):
	print(" ")
	print("  >> Prefix to be %s: <<" % prefix_add_remove)
	print("  => ", end="")
	s_prefixes_add_remove_i = input()
	s_prefixes_add_remove_i = s_prefixes_add_remove_i.strip()
	s_prefixes_add_remove_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$', s_prefixes_add_remove_i)
	while s_prefixes_add_remove_re is None:
		print("  !! IP address has incorrect format. Type again. !!\n")
		print("  >> Prefix to be %s: <<" % prefix_add_remove)
		print("  => ", end="")
		s_prefixes_add_remove_i = input()
		s_prefixes_add_remove_i = s_prefixes_add_remove_i.strip()
		s_prefixes_add_remove_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$', s_prefixes_add_remove_i)
		if s_prefixes_add_remove_re is not None:
			if append_remove is 'append':
				gd_prefixes_in_list_toupdate['entries'].append({
					'ipPrefix': s_prefixes_add_remove_i
				})
				return gd_prefixes_in_list_toupdate
			if append_remove is 'remove':
				gd_prefixes_in_list_toupdate['entries'].remove({
					'ipPrefix': s_prefixes_add_remove_i
				})
				return gd_prefixes_in_list_toupdate

	if append_remove is 'append':
		gd_prefixes_in_list_toupdate['entries'].append({
			'ipPrefix': s_prefixes_add_remove_i
		})
		return gd_prefixes_in_list_toupdate

	if append_remove is 'remove':
		gd_prefixes_in_list_toupdate['entries'].remove({
			'ipPrefix': s_prefixes_add_remove_i
		})
		return gd_prefixes_in_list_toupdate

# --- compare present prefix list with updated prefix list ---- #
def prefixes_in_list_compare_present_updated():
	l_prefixes_present = []
	l_prefixes_updated = []
	for s_pilp in gd_prefixes_in_list_present['entries']:
		l_prefixes_present.append(s_pilp['ipPrefix'].strip())

	for s_pilu in gd_prefixes_in_list_updated['entries']:
		l_prefixes_updated.append(s_pilu['ipPrefix'].strip())

	l_prefixes_present.insert(0, "before:")
	l_prefixes_updated.insert(0, "after:")
	os.system("clear")
	print("\n")
	for s_pilp_pilu in list(itertools.zip_longest(l_prefixes_present, l_prefixes_updated, fillvalue=' ')):
		s_pilp_pilu_fmt = '  {:<31}{:<31}'.format(s_pilp_pilu[0], s_pilp_pilu[1])
		print(s_pilp_pilu_fmt)

# --- add/remove more prefixes  --- #
def prefix_add_remove_more_records(prefix_add_remove,prefix_from_to,append_remove):
	print("\n")
	print("  >> %s another prefix %s list? (y/n): <<" % (prefix_add_remove,prefix_from_to))
	print("  => ", end="")

	s_add_remove_prefix_to_list_i = input()
	s_add_remove_prefix_to_list_re = re.search('[y|n]', s_add_remove_prefix_to_list_i)
	while s_add_remove_prefix_to_list_re is None:
		print("  !! Select from above options. Please try again: !!")
		print("  => ", end="")
		s_add_remove_prefix_to_list_i = input()
		s_add_remove_prefix_to_list_re = re.search('[y|n]', s_add_remove_prefix_to_list_i)
		if s_add_remove_prefix_to_list_i is "y":
			if append_remove is 'append':
				prefixes_add_remove('added', 'to', 'append')
				prefixes_in_list_compare_present_updated()
				prefix_add_remove_more_records('Add', 'to', 'append')
				return
			if append_remove is 'remove':
				prefixes_add_remove('removed','from','remove')
				prefixes_in_list_compare_present_updated()
				prefix_add_remove_more_records('Remove','from','remove')
				return
		if s_add_remove_prefix_to_list_i is "n":
			return
	if s_add_remove_prefix_to_list_i is "y":
		if append_remove is 'append':
			prefixes_add_remove('added','to','append')
			prefixes_in_list_compare_present_updated()
			prefix_add_remove_more_records('Add','to','append')
			return
		if append_remove is 'remove':
			prefixes_add_remove('removed','from','remove')
			prefixes_in_list_compare_present_updated()
			prefix_add_remove_more_records('Remove','from','remove')
			return
	if s_add_remove_prefix_to_list_i is "n":
		return

# --- commit changes y/n --- #
def commit_changes_yn():
	print("\n")
	print("  >> Write data to vManage? <<")
	print("     'commit'  | commit changes")
	print("     'n'       | exit")
	print("  => ", end="")
	s_commit_changes_yn_i = input()
	s_commit_changes_yn_re = re.search('commit|n', s_commit_changes_yn_i)
	while s_commit_changes_yn_re is None:
		print("  !! Select from above options. Please try again: !!")
		print("  => ", end="")
		s_commit_changes_yn_i = input()
		if s_commit_changes_yn_i == 'commit':
			return('commit')
		if s_commit_changes_yn_i == "n":
			exit()
	if s_commit_changes_yn_i == 'commit':
		return ('commit')
	if s_commit_changes_yn_i == "n":
		exit()

# --- commit changes --- #
def commit_changes_add_remove(s_session, d_conf):
	os.system("clear")
	print("\n")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/policy/list/dataprefix/' + gl_prefix_list_id
	headers={'Content-Type': 'application/json'}
	payload = json.dumps(gd_prefixes_in_list_updated)
	r = gs_session.put(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("  HTTP Status Code - " + r.status_code)
		d_commit_changes_add_remove_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_commit_changes_add_remove_error_message, indent=2, sort_keys=True))
		exit()
	d_commit_changes_add_remove_message = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_commit_changes_add_remove_message, indent=2, sort_keys=True))

	for k, v in d_commit_changes_add_remove_message.items():
		if 'masterTemplatesAffected' in k:
			print('  masterTemplatesAffected:')
			if v:
				for mt in v:
					print(' ', mt)
			else:
				print('  - none')
				print('  - change completed')
				print('\n')
		if 'processId' in k:
			print('  processId:')
			print(' ', v)

	return(d_commit_changes_add_remove_message)

# --- activate changes --- #
def activate_changes(s_session, d_conf):
	l_vmanage_master_templates_affected = []
	# print(gd_commit_changes_add_remove_message['processId'])
	for s_ccadm in gd_commit_changes_add_remove_message['masterTemplatesAffected']:
		# print(d_vmanage_master_templates_affected['processId'])
		l_vmanage_master_templates_affected.append(s_ccadm)

	l_devicetemplatelist = []
	d_devicetemplatelist = {}
	l_vmanage_template_config_input = []
	for s_vmta in l_vmanage_master_templates_affected:
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device/config/attached/' + s_vmta
		r = s_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vmanage_config_attached_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vmanage_config_attached_error_message, indent=2, sort_keys=True))
			exit()
		d_vmanage_config_attached = json.loads(r.content.decode('utf8'))
		# print(json.dumps(d_vmanage_attached_template, indent=2, sort_keys=True))
		for s_vca in d_vmanage_config_attached['data']:
			# print(s_vca['host-name'])
			# print(s_vca['deviceIP'])
			# print(s_vca['site-id'])
			# print(s_vca['uuid'])
			d_vmanage_template_config_input = {"isEdited": True, "templateId": "none",
			 "deviceIds": ["none"], "isMasterEdited": False}
			d_vmanage_template_config_input.update({'templateId':s_vmta})
			l_vmanage_template_config_input.append(s_vca['uuid'])
			d_vmanage_template_config_input.update({'deviceIds':l_vmanage_template_config_input})
			# print (d_vmanage_template_config_input)

			url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device/config/input/'
			headers = {'Content-Type': 'application/json'}
			payload = json.dumps(d_vmanage_template_config_input)
			r = s_session.post(url=url, data=payload, headers=headers, verify=False)
			r.status_code = str(r.status_code)
			r.status_code = r.status_code.strip()
			if '200' not in r.status_code:
				print("\n")
				print("  HTTP Status Code - " + r.status_code)
				d_vmanage_config_input_error_message = json.loads(r.content.decode('utf8'))
				print(json.dumps(d_vmanage_config_input_error_message, indent=2, sort_keys=True))
				exit()
			d_vmanage_config_input = json.loads(r.content.decode('utf8'))
			# print(json.dumps(d_vmanage_config_input, indent=2, sort_keys=True))

			for s_vci in d_vmanage_config_input['data']:
				s_vci.update({'csv-templateId':s_vmta})
			# print(d_vmanage_config_input['data'])
			d_templatelist = {'templateId':s_vmta}
			d_templatelist.update({'device': d_vmanage_config_input['data']})
			d_templatelist.update({'isEdited':True})
			s_vmanage_templatelist = d_templatelist
			l_devicetemplatelist.append(s_vmanage_templatelist)

		del l_vmanage_template_config_input[:]
	d_devicetemplatelist.update({'deviceTemplateList':l_devicetemplatelist})
	# print(d_devicetemplatelist)

	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/device/config/attachcli'
	headers = {'Content-Type': 'application/json'}
	payload = json.dumps(d_devicetemplatelist)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("\n")
		print("  HTTP Status Code - " + r.status_code)
		d_vmanage_template_list_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_vmanage_template_list_error_message, indent=2, sort_keys=True))
		exit()
	d_vmanage_template_list = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_vmanage_template_list, indent=2, sort_keys=True))
	push_config_id = d_vmanage_template_list['id']
	print("\n")
	print(' ',push_config_id,'\n')

	c_tasks_status = 0
	while c_tasks_status < 2:
		c_tasks_status = 0
		time.sleep(20)
		url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/device/action/status/' + push_config_id
		r = s_session.get(url=url, verify=False)
		r.status_code = str(r.status_code)
		r.status_code = r.status_code.strip()
		if '200' not in r.status_code:
			print("\n")
			print("  HTTP Status Code - " + r.status_code)
			d_vmanage_action_status_error_message = json.loads(r.content.decode('utf8'))
			print(json.dumps(d_vmanage_action_status_error_message, indent=2, sort_keys=True))
			exit()
		d_vmanage_action_status = json.loads(r.content.decode('utf8'))

		os.system("clear")
		l_status_char_len = []
		l_status_change = []
		for s_rts in d_vmanage_action_status['data']:
			if 'Success' in s_rts['status'] or 'Fail' in s_rts['status']:
				c_tasks_status += 1
			l_status_char_len.append(len(s_rts['system-ip']))
			l_status_char_len.append(len(s_rts['host-name']))
			l_status_char_len.append(len(s_rts['currentActivity']))
			l_status_char_len.append(len(s_rts['status']))
			# l_status_change.append('  vBond IP:    ' + str(s_rts['system-ip']))
			l_status_change.append('  vBond:    ' + str(s_rts['host-name']))
			l_status_change.append('  activity: ' + str(s_rts['currentActivity']))
			l_status_change.append('  status:   ' + str(s_rts['status']))
			l_status_change.append('\n')

		l_status_char_len = sorted(l_status_char_len, reverse=True)
		del l_status_change[-1:]
		l_status_change.insert(0,'  ========= ' + l_status_char_len[0] * '=')
		l_status_change.insert(0,' ')
		l_status_change.insert(0,'\n')
		l_status_change.append('  ========= ' + l_status_char_len[0] * '=')

		for s_sc in l_status_change:
			print(s_sc)
		del l_status_char_len[:]
		del l_status_change[:]
	print("\n")

# --- create new data prefix list and add prefix --- #
def create_prefix_list_add_new_prefix():
	os.system("clear")
	print("\n")
	print("  >> Add new data prefix list: <<\n")
	s_create_prefix_list_i = input('  - Data prefix list name: ')
	s_create_prefix_list_re = re.search('\w',s_create_prefix_list_i)
	while s_create_prefix_list_re is None:
		print("  !! Prefix list has incorrect name. Type again. !!\n")
		s_create_prefix_list_i = input('  - Data prefix list name: ')
		s_create_prefix_list_re = re.search('\w',s_create_prefix_list_i)

	s_add_new_prefix_i = input('  - Prefix to be added: ')
	s_add_new_prefix_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$', s_add_new_prefix_i)

	while s_add_new_prefix_re is None:
		print("  !! IP address has incorrect format. Type again. !!\n")
		s_add_new_prefix_i = input('  - Prefix to be added: ')
		s_add_new_prefix_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$',s_add_new_prefix_i)
		if s_add_new_prefix_re is not None:
			d_create_prefix_list_form = b'{"listId":"","name":"","type":"dataPrefix","description":"Desc Not Required","entries":[],"lastUpdated":"","owner":"","readOnly":false,"version":"0","referenceCount":0,"isActivatedByVsmart":true}'
			gd_prefixes_in_list_toupdate = json.loads(d_create_prefix_list_form.decode('utf8'))
			gd_prefixes_in_list_toupdate['name'] = s_create_prefix_list_i
			gd_prefixes_in_list_toupdate['entries'].append({
				'ipPrefix': s_add_new_prefix_i
				})
			return gd_prefixes_in_list_toupdate

	if s_add_new_prefix_re is not None:
		d_create_prefix_list_form = b'{"listId":"","name":"","type":"dataPrefix","description":"Desc Not Required","entries":[],"lastUpdated":"","owner":"","readOnly":false,"version":"0","referenceCount":0,"isActivatedByVsmart":true}'
		gd_prefixes_in_list_toupdate = json.loads(d_create_prefix_list_form.decode('utf8'))
		gd_prefixes_in_list_toupdate['name'] = s_create_prefix_list_i
		gd_prefixes_in_list_toupdate['entries'].append({
		'ipPrefix': s_add_new_prefix_i
		})
		return gd_prefixes_in_list_toupdate

# --- add records --- #
def create_prefix_list_more_records():
	print(' ')
	print("  >> Add another prefix? (y/n): <<")
	print("  => ", end="")
	s_add_prefix_to_list_i = input()
	s_add_prefix_to_list_re = re.search('[y|n]', s_add_prefix_to_list_i)
	while s_add_prefix_to_list_re is None:
		print("  !! Select from above options. Please try again: !!")
		print("  => ", end="")
		s_add_prefix_to_list_i = input()
		s_add_prefix_to_list_re = re.search('[y|n]', s_add_prefix_to_list_i)
		if s_add_prefix_to_list_i is "y":
			create_prefix_list_prefixes_add()
			create_prefix_print_list()
			create_prefix_list_more_records()
			return
		if s_add_prefix_to_list_i is "n":
			return
	if s_add_prefix_to_list_i is "y":
		create_prefix_list_prefixes_add()
		create_prefix_print_list()
		create_prefix_list_more_records()
		return
	if s_add_prefix_to_list_i is "n":
		return

# --- add prefixes --- #
def create_prefix_list_prefixes_add():
	print(' ')
	print("  >> Provide prefix to be added: <<")
	print("  => ", end="")
	s_prefixes_add_i = input()
	s_prefixes_add_i = s_prefixes_add_i.strip()
	s_prefixes_add_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$', s_prefixes_add_i)
	while s_prefixes_add_re is None:
		print(" ")
		print("  !! IP address has incorrect format. Type again. !!")
		print("  => ", end="")
		s_prefixes_add_i = input()
		s_prefixes_add_i = s_prefixes_add_i.strip()
		s_prefixes_add_re = re.search('^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})/\d{2}$', s_prefixes_add_i)
		if s_prefixes_add_re is not None:
			gd_prefixes_in_list_toupdate['entries'].append({
				'ipPrefix': s_prefixes_add_i
			})
			return gd_prefixes_in_list_toupdate

	gd_prefixes_in_list_toupdate['entries'].append({
		'ipPrefix': s_prefixes_add_i
	})
	return gd_prefixes_in_list_toupdate


# --- print list --- #
def create_prefix_print_list():
	l_prefixes_updated = []
	for s_pilp in gd_prefixes_in_list_toupdate['entries']:
		l_prefixes_updated.append(s_pilp['ipPrefix'].strip())
	os.system("clear")
	print("\n")
	for s_pu in l_prefixes_updated:
		print('  ',s_pu)
	print(" ")

# --- commit new data prefix list --- #
def commit_changes_create_prefix_list(s_session, d_conf):
	os.system("clear")
	url = 'https://' + d_conf['vmanage_ip'] + '/dataservice/template/policy/list/dataprefix/'
	headers={'Content-Type': 'application/json'}
	payload = json.dumps(gd_prefixes_in_list_toupdate)
	r = s_session.post(url=url, data=payload, headers=headers, verify=False)
	r.status_code = str(r.status_code)
	r.status_code = r.status_code.strip()
	if '200' not in r.status_code:
		print("  HTTP Status Code - " + r.status_code)
		d_commit_changes_create_list_error_message = json.loads(r.content.decode('utf8'))
		print(json.dumps(d_commit_changes_create_list_error_message, indent=2, sort_keys=True))
		exit()
	d_commit_changes_create_list_message = json.loads(r.content.decode('utf8'))
	# print(json.dumps(d_commit_changes_create_list_message, indent=2, sort_keys=True))
	s_push_create_list_id = d_commit_changes_create_list_message['listId']
	print(2* "\n")
	print('  ',s_push_create_list_id)
	print('   completed ...','\n')

# --- main menu --- #
os.system("clear")
print("\n")
print("   1. New    | new data prefix list ")
print("   2. Add    | add prefix to existing prefix list")
print("   3. Remove | remove prefix from existing prefix list")
print("   4. Exit\n")
print("  => ", end="")
s_main_menu_i = input()
s_main_menu_re = re.search('[1234]', s_main_menu_i)
while s_main_menu_re is None:
	print("  !! select from above options. please try again: !!")
	print("  => ", end="")
	s_main_menu_i = input()

	if s_main_menu_i is "1":
		gs_session, gd_conf = authentication.login()
		gd_prefixes_in_list_toupdate = create_prefix_list_add_new_prefix()
		create_prefix_list_more_records()
		commit_changes_yn()
		commit_changes_create_prefix_list(gs_session, gd_conf)

	if s_main_menu_i is "2":
		gs_session, gd_conf = authentication.login()
		(gl_prefix_list_id, gl_prefix_list_name) = prefix_lists_and_prefix_list_id(gs_session, gd_conf)
		(gd_prefixes_in_list_present,gd_prefixes_in_list_toupdate) = prefixes_in_list(gs_session, gd_conf)
		prefixes_add_remove_yn('Add','to')
		gd_prefixes_in_list_updated = prefixes_add_remove('added','to','append')
		prefixes_in_list_compare_present_updated()
		prefix_add_remove_more_records('Add','to','append')
		commit_changes_yn()
		gd_commit_changes_add_remove_message = commit_changes_add_remove(gs_session, gd_conf)
		if 'processId' in gd_commit_changes_add_remove_message:
			activate_changes(gs_session, gd_conf)

	if s_main_menu_i is "3":
		gs_session, gd_conf = authentication.login()
		(gl_prefix_list_id, gl_prefix_list_name) = prefix_lists_and_prefix_list_id(gs_session, gd_conf)
		(gd_prefixes_in_list_present, gd_prefixes_in_list_toupdate) = prefixes_in_list()
		prefixes_add_remove_yn('Remove', 'from')
		gd_prefixes_in_list_updated = prefixes_add_remove('removed','from','remove')
		prefixes_in_list_compare_present_updated()
		prefix_add_remove_more_records('Remove', 'from','remove')
		commit_changes_yn()
		gd_commit_changes_add_remove_message = commit_changes_add_remove(gs_session, gd_conf)
		if 'processId' in gd_commit_changes_add_remove_message:
			activate_changes(gs_session, gd_conf)

	if s_main_menu_i is "4":
		exit()


if s_main_menu_i is "1":
	gs_session, gd_conf = authentication.login()
	gd_prefixes_in_list_toupdate = create_prefix_list_add_new_prefix()
	create_prefix_list_more_records()
	commit_changes_yn()
	commit_changes_create_prefix_list(gs_session, gd_conf)

if s_main_menu_i is "2":
	gs_session, gd_conf = authentication.login()
	(gl_prefix_list_id, gl_prefix_list_name) = prefix_lists_and_prefix_list_id(gs_session, gd_conf)
	(gd_prefixes_in_list_present, gd_prefixes_in_list_toupdate) = prefixes_in_list(gs_session, gd_conf)
	prefixes_add_remove_yn('Add', 'to')
	gd_prefixes_in_list_updated = prefixes_add_remove('added','to','append')
	prefixes_in_list_compare_present_updated()
	prefix_add_remove_more_records('Add','to','append')
	commit_changes_yn()
	gd_commit_changes_add_remove_message = commit_changes_add_remove(gs_session, gd_conf)
	if 'processId' in gd_commit_changes_add_remove_message:
		activate_changes(gs_session, gd_conf)


if s_main_menu_i is "3":
	gs_session, gd_conf = authentication.login()
	(gl_prefix_list_id, gl_prefix_list_name) = prefix_lists_and_prefix_list_id(gs_session, gd_conf)
	(gd_prefixes_in_list_present, gd_prefixes_in_list_toupdate) = prefixes_in_list(gs_session, gd_conf)
	prefixes_add_remove_yn('Remove', 'from')
	gd_prefixes_in_list_updated = prefixes_add_remove('removed','from','remove')
	prefixes_in_list_compare_present_updated()
	prefix_add_remove_more_records('Remove', 'from','remove')
	commit_changes_yn()
	gd_commit_changes_add_remove_message = commit_changes_add_remove(gs_session, gd_conf)
	if 'processId' in gd_commit_changes_add_remove_message:
		activate_changes(gs_session, gd_conf)

if s_main_menu_i is "4":
	exit()


