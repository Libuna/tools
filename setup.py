#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import os
import re
import json
import getpass
import binascii
import ipaddress
from cryptography.fernet import Fernet

# --- header --- #
def header():
	print("""
  
  ================================
  Viptela automation tools: Setup
  v.1.1 by slavali
  ================================
	""")

# --- instructions to follow --- #
def instructions():
	print("""

				Welcome to initial settings for Viptela automation tools. 


  You will need to provide all these below information which will be stored in ~/viptela/.conf file located 
  in your home folder used only by automation tools. Config file can either be in clear text or encrypted. 
  This guide will navigate you and help to complete necessary steps. 


  vManage / vEdge:
  - vManage IP address       
  - vManage username
  - vManage password
  - transport colors over internet
  - transport colors over mpls
  - vEdge image version                          (e.g: 18.4.5)
  - vEdge vpn id for customer / internal network (e.g: vpn 1)
  - routable IP address in customer's vpn for ping tests
  
  Cisco:
  - Cisco account username
  - Cisco account password
  - Cisco client ID        (used for API access)
  - Cisco client secret    (used for API access)
  - Cisco smart account    (e.g: sdwan.verizon.com)
  - Cisco virtual account  
  
  Misc:
  - Your email address     (used by reports)
   
	""")
	input('  Press Enter to continue...')
	os.system("clear")

	print("""

  Step 1: 

  Create Cisco "client id" and "client secret" for API calls.

  - open and login to URL with your Cisco credentials: https://apidocs-prod.cisco.com/?api=Smart%20Accounts
  - click on "Request API Access"
  - click on "Register New Application"
  - put Application name (choose any names), mark "Resource Owner Grant" in "OAuth Grant Types" and click "Register"
  - Cisco site will generate your Cisco "client id" and "client secret" values.


	""")
	input('  Press Enter to continue...')
	os.system("clear")

	print("""

  Step 2: 

  Validate your access to Cisco smart and virtual accounts.

  - open and login to URL with your Cisco credentials: https://software.cisco.com
  - click on "Plug and Play Connect" in "Network Plug and Play" tab
  - choose smart account (e.g: sdwan.verizon.com)
  - choose virtual account of your project
  - if you can read serial numbers in virtual account you have appropriate permissions

	""")
	input('  Press Enter to continue...')
	os.system("clear")

	print("""

  Step 3: 

  Install additional Python modules.
  
  - requests
  - netaddr
  - colorama
  - netmiko 

  run these commands on domain server:
  /home/repos/public/Python/bin/python3.6 /home/repos/public/Python/bin/pip install --user requests
  /home/repos/public/Python/bin/python3.6 /home/repos/public/Python/bin/pip install --user netaddr
  /home/repos/public/Python/bin/python3.6 /home/repos/public/Python/bin/pip install --user colorama
  /home/repos/public/Python/bin/python3.6 /home/repos/public/Python/bin/pip install --upgrade --user netmiko
  
	""")
	input('  Press Enter to continue...')
	os.system("clear")
	print("""
	
  It's very important to provide all valid information in order to have the tools properly working.
  
  Do you have all information available? (y/n):
	""")
	print("  => ", end="")
	s_answer = input()
	s_answer_re = re.search('^y$|^n$', s_answer)
	while s_answer_re is None:
		print("  !! Select from above options. Please try again: !!")
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)

	if s_answer is "y":
		return 'y'
	if s_answer is "n":
		os.system("clear")
		print('\n')
		print('  Please complete all the instructions and run the script again.\n')
		print('\n')
		exit()

# --- ip address validation --- #
def ip_validation(s_ip_address):
	while True:
		try:
			s_ip = ipaddress.ip_address(s_ip_address)
		except ValueError:
			print("  ! IP has incorrect format !\n")
			print("  => ", end="")
			s_ip_address = input()
		else:
			break

	return s_ip_address

# --- create or update config file --- #
def conf_file(create_or_update):
	os.system("clear")
	d_conf = {}
	d_conf.update({'userpath': gs_userpath})
	s_key = ''
	if 'update' in create_or_update:
		f_conf = open(gs_conffile, 'r')
		f_conf_read = f_conf.read()
		if 'vmanage_ip' in f_conf_read:
			d_conf = json.loads(f_conf_read)
			f_conf.close()
		else:
			print('\n')
			print('  DECRYPTION KEY: ')
			s_key = getpass.getpass('').encode()
			print('\n')
			e_conf = f_conf_read.encode()
			f_conf.close()
			try:
				decryption = Fernet(s_key)
				j_conf = decryption.decrypt(e_conf).decode()
				d_conf = json.loads(j_conf)
			except binascii.Error as err:
				os.system("clear")
				print('\n')
				print('  DECRYPTION key is invalid. ')
				print('\n')
				exit()
			except ValueError:
				os.system("clear")
				print('\n')
				print('  DECRYPTION key is invalid. ')
				print('\n')
				exit()

	c_update = 0
	os.system("clear")
	print('\n')
	if not 'update' in create_or_update:
		print('  Please provide following information:\n')

	print('  vManage IP address:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW vManage IP address:')
			print("  => ", end="")
			s_vmanage_ip = input()
			s_ip_address = ip_validation(s_vmanage_ip)
			d_conf.update({'vmanage_ip': s_ip_address})
	else:
		print("  => ", end="")
		s_vmanage_ip = input()
		s_ip_address = ip_validation(s_vmanage_ip)
		d_conf.update({'vmanage_ip': s_ip_address})

	os.system("clear")
	print('\n')
	print('  vManage username:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW vManage username:')
			print("  => ", end="")
			s_vmanage_username = input()
			while not s_vmanage_username:
				print("  !! Username can't be empty.\n")
				print("  => ", end="")
				s_vmanage_username = input()
			d_conf.update({'vmanage_username': s_vmanage_username})
	else:
		print("  => ", end="")
		s_vmanage_username = input()
		while not s_vmanage_username:
			print("  !! Username can't be empty.\n")
			print("  => ", end="")
			s_vmanage_username = input()
		d_conf.update({'vmanage_username': s_vmanage_username})

	os.system("clear")
	print('\n')
	print('  vManage password (hidden):')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW vManage password (hidden):')
			s_vmanage_password = getpass.getpass('')
			while not s_vmanage_password:
				print("  !! Password can't be empty.\n")
				s_vmanage_password = getpass.getpass('')
			d_conf.update({'vmanage_password': s_vmanage_password})
	else:
		s_vmanage_password = getpass.getpass('')
		while not s_vmanage_password:
			print("  !! Password can't be empty.\n")
			s_vmanage_password = getpass.getpass('')
		d_conf.update({'vmanage_password': s_vmanage_password})

	os.system("clear")
	print('\n')
	print('  Internet transport colors:')
	if 'create' in create_or_update:
		print('  (use comma "," between colors. e.g: biz-internet,public-internet)')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update += 1
			print('\n')
			print('  NEW internet transport colors:')
			print('  (use comma , between colors. e.g: biz-internet,public-internet)')
			print("  => ", end="")
			s_vedge_internet_color = input()
			while not s_vedge_internet_color:
				print("  !! Colors can't be empty.\n")
				print("  => ", end="")
				s_vedge_internet_color = input()
			d_conf.update({'internet_color': s_vedge_internet_color})
	else:
		print("  => ", end="")
		s_vedge_internet_color = input()
		while not s_vedge_internet_color:
			print("  !! Colors can't be empty.\n")
			print("  => ", end="")
			s_vedge_internet_color = input()
		d_conf.update({'internet_color': s_vedge_internet_color})

	os.system("clear")
	print('\n')
	print('  Mpls transport colors:')
	if 'create' in create_or_update:
		print('  (use comma "," between colors. e.g: mpls,private1)')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update += 1
			print('\n')
			print('  NEW mpls transport colors:')
			print('  (use comma , between colors. e.g: mpls,private1)')
			print("  => ", end="")
			s_vedge_mpls_color = input()
			while not s_vedge_mpls_color:
				print("  !! Colors can't be empty.\n")
				print("  => ", end="")
				s_vedge_mpls_color = input()
			d_conf.update({'mpls_color': s_vedge_mpls_color})
	else:
		print("  => ", end="")
		s_vedge_mpls_color = input()
		while not s_vedge_mpls_color:
			print("  !! Colors can't be empty.\n")
			print("  => ", end="")
			s_vedge_mpls_color = input()
		d_conf.update({'mpls_color': s_vedge_mpls_color})

	os.system("clear")
	print('\n')
	print('  vEdge image version:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW vEdge OS version:')
			print("  => ", end="")
			s_vedge_os_version = input()
			while not s_vedge_os_version:
				print("  !! Image version can't be empty.\n")
				print("  => ", end="")
				s_vedge_os_version = input()
			d_conf.update({'vedge_image_version': s_vedge_os_version})
	else:
		print("  => ", end="")
		s_vedge_os_version = input()
		while not s_vedge_os_version:
			print("  !! Image version can't be empty.\n")
			print("  => ", end="")
			s_vedge_os_version = input()
		d_conf.update({'vedge_image_version': s_vedge_os_version})

	os.system("clear")
	print('\n')
	print('  VPN id for customer (internal) network (e.g: 1):')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update += 1
			print('\n')
			print('  NEW VPN id:')
			print("  => ", end="")
			s_vpn_id_lan = input()
			while not s_vpn_id_lan:
				print("  !! VPN id can't be empty.\n")
				print("  => ", end="")
				s_vpn_id_lan = input()
			d_conf.update({'vpn_id_lan': s_vpn_id_lan})
	else:
		print("  => ", end="")
		s_vpn_id_lan = input()
		while not s_vpn_id_lan:
			print("  !! VPN id can't be empty.\n")
			print("  => ", end="")
			s_vpn_id_lan = input()
		d_conf.update({'vpn_id_lan': s_vpn_id_lan})

	os.system("clear")
	print('\n')
	print("  Routable IP address in customer's vpn for PING test:")
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW IP address:')
			print("  => ", end="")
			s_lan_ip_ping = input()
			s_ip_address = ip_validation(s_lan_ip_ping)
			d_conf.update({'lan_ip_ping': s_ip_address})
	else:
		print("  => ", end="")
		s_lan_ip_ping = input()
		s_ip_address = ip_validation(s_lan_ip_ping)
		d_conf.update({'lan_ip_ping': s_ip_address})

	os.system("clear")
	print('\n')
	print('  Cisco username:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco username:')
			print("  => ", end="")
			s_cisco_username = input('')
			while not s_cisco_username:
				print("  !! Username can't be empty.\n")
				print("  => ", end="")
				s_cisco_username = input()
			d_conf.update({'cisco_username': s_cisco_username})
	else:
		print("  => ", end="")
		s_cisco_username = input('')
		while not s_cisco_username:
			print("  !! Username can't be empty.\n")
			print("  => ", end="")
			s_cisco_username = input()
		d_conf.update({'cisco_username': s_cisco_username})

	os.system("clear")
	print('\n')
	print('  Cisco password (hidden):')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco password (hidden):')
			s_cisco_password = getpass.getpass('')
			while not s_cisco_password:
				print("  !! Password can't be empty.\n")
				s_cisco_password = getpass.getpass('')
			d_conf.update({'cisco_password': s_cisco_password})
	else:
		s_cisco_password = getpass.getpass('')
		while not s_cisco_password:
			print("  !! Password can't be empty.\n")
			s_cisco_password = getpass.getpass('')
		d_conf.update({'cisco_password': s_cisco_password})

	os.system("clear")
	print('\n')
	print('  Cisco client id:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco client id:')
			print("  => ", end="")
			s_cisco_client_id = input()
			while not s_cisco_client_id:
				print("  !! Client id can't be empty.\n")
				print("  => ", end="")
				s_cisco_client_id = input()
			d_conf.update({'cisco_client_id': s_cisco_client_id})
	else:
		print("  => ", end="")
		s_cisco_client_id = input()
		while not s_cisco_client_id:
			print("  !! Client id can't be empty.\n")
			print("  => ", end="")
			s_cisco_client_id = input()
		d_conf.update({'cisco_client_id': s_cisco_client_id})

	os.system("clear")
	print('\n')
	print('  Cisco client secret (hidden):')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco client secret (hidden):')
			s_cisco_client_secret = getpass.getpass('')
			while not s_cisco_client_secret:
				print("  !! Secret id can't be empty.\n")
				s_cisco_client_secret = getpass.getpass('')
			d_conf.update({'cisco_client_secret': s_cisco_client_secret})
	else:
		s_cisco_client_secret = getpass.getpass('')
		while not s_cisco_client_secret:
			print("  !! Secret id can't be empty.\n")
			s_cisco_client_secret = getpass.getpass('')
		d_conf.update({'cisco_client_secret': s_cisco_client_secret})

	os.system("clear")
	print('\n')
	print('  Cisco smart account:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco smart account:')
			print("  => ", end="")
			s_cisco_smart_account = input()
			while not s_cisco_smart_account:
				print("  !! Smart account can't be empty.\n")
				print("  => ", end="")
				s_cisco_smart_account = input()
			d_conf.update({'cisco_smart_account': s_cisco_smart_account})
	else:
		print("  => ", end="")
		s_cisco_smart_account = input()
		while not s_cisco_smart_account:
			print("  !! Smart account can't be empty.\n")
			print("  => ", end="")
			s_cisco_smart_account = input()
		d_conf.update({'cisco_smart_account': s_cisco_smart_account})

	os.system("clear")
	print('\n')
	print('  Cisco virtual account:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Cisco virtual account:')
			print("  => ", end="")
			s_cisco_virtual_account = input()
			while not s_cisco_virtual_account:
				print("  !! Virtual account can't be empty.\n")
				print("  => ", end="")
				s_cisco_virtual_account = input()
			d_conf.update({'cisco_virtual_account': s_cisco_virtual_account})
	else:
		print("  => ", end="")
		s_cisco_virtual_account = input()
		while not s_cisco_virtual_account:
			print("  !! Virtual account can't be empty.\n")
			print("  => ", end="")
			s_cisco_virtual_account = input()
		d_conf.update({'cisco_virtual_account': s_cisco_virtual_account})

	os.system("clear")
	print('\n')
	print('  Your email address:')
	if 'update' in create_or_update:
		print('\n')
		print('  Do you want to update? (y/n)')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		if s_answer is "y":
			c_update  += 1
			print('\n')
			print('  NEW Your email address:')
			print("  => ", end="")
			s_my_email = input()
			s_my_email = s_my_email.strip()
			s_my_email_re = re.search('@.*\..*', s_my_email)
			while s_my_email_re is None:
				print("  !! Email has incorrect format.\n")
				print("  => ", end="")
				s_my_email = input()
				s_my_email = s_my_email.strip()
				s_my_email_re = re.search('@.*\..*', s_my_email)
			d_conf.update({'my_email': s_my_email})
	else:
		print("  => ", end="")
		s_my_email = input()
		s_my_email = s_my_email.strip()
		s_my_email_re = re.search('@.*\..*', s_my_email)
		while s_my_email_re is None:
			print("  !! Email has incorrect format.\n")
			print("  => ", end="")
			s_my_email = input()
			s_my_email = s_my_email.strip()
			s_my_email_re = re.search('@.*\..*', s_my_email)
		d_conf.update({'my_email': s_my_email})

	return d_conf, c_update, s_key

# --- save file (clear / encrypted) --- #
def save_file():
	os.system("clear")
	if gc_update > 0:
		if not gs_key:
				f_conf = open(gs_conffile, 'w')
				json.dump(gd_conf, f_conf)
				f_conf.close()
		else:
			f_conf = open(gs_conffile, 'w')
			encryption = Fernet(gs_key)
			j_conf = json.dumps(gd_conf).encode()
			e_conf = encryption.encrypt(j_conf)
			s_conf = e_conf.decode()
			f_conf.write(s_conf)
			f_conf.close()
		print('\n')
		print('  Records have been updated.')
		print('\n')

	if not gs_userfile:
		print('\n')
		print('  Do you want to encrypt configuration file (y/n)?.\n')
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)
		while s_answer_re is None:
			print("  !! Select (y/n):\n")
			print("  => ", end="")
			s_answer = input()
			s_answer_re = re.search('^y$|^n$', s_answer)

		os.system("clear")
		if s_answer is "y":
			s_key = Fernet.generate_key()
			f_conf = open(gs_conffile, 'w')
			j_conf = json.dumps(gd_conf).encode()
			encryption = Fernet(s_key)
			e_conf = encryption.encrypt(j_conf)
			s_conf = e_conf.decode()
			f_conf.write(s_conf)
			f_conf.close()
			s_key_print = s_key.decode()
			print("""
  
  Encrypted records have been saved successfully.
  
  !!!!! DECRYPTION KEY : %s
  
  Save the key. Whenever Viptela tools will run you will be asked for decryption key.
  
  Tip:
  In SecureCRT on the bottom line next to "Default" right click and choose "New Button...
  Put the key to "Send String" window and press "OK". New button will be on a tray
  which you can simply anytime click on when Viptela tools will ask for key.
  
  For record updates in a file just run ./setup script again.
  If you will loose the key just delete ~/viptela/.conf file and run ./setup script.
   
   
   
			""" % s_key_print)
			os.chmod(gs_conffile, 0o600)
			os.chmod(gs_userpath + '/viptela', 0o700)

		if s_answer is "n":
			print("""
		
  Clear text records have been saved successfully.
  
  If you will need to update records in a file just run ./setup script again.



			""")
			f_conf = open(gs_conffile, 'w')
			json.dump(gd_conf, f_conf)
			f_conf.close()
			os.chmod(gs_conffile, 0o600)
			os.chmod(gs_userpath + '/viptela', 0o700)


# --- main --- #
os.system("clear")
gs_userpath = os.path.expanduser('~')
gs_userfile = os.path.isfile(gs_userpath + '/viptela/.conf')
gs_conffile = gs_userpath + '/viptela/.conf'
gs_answer = ''
if not gs_userfile:
	header()
	gs_answer = instructions()
else:
	header()
	print('  Configuration file exists. Do you want to update it? (y/n)')
	print("  => ", end="")
	s_answer = input()
	s_answer_re = re.search('^y$|^n$', s_answer)
	while s_answer_re is None:
		print("  !! Select (y/n):\n")
		print("  => ", end="")
		s_answer = input()
		s_answer_re = re.search('^y$|^n$', s_answer)

	if s_answer is "y":
		gd_conf, gc_update, gs_key = conf_file('update')
		save_file()

	if s_answer is "n":
		print('\n')
		os.system("clear")
		exit()

if gs_answer == 'y':
	gd_conf, gc_update, gs_key = conf_file('create')
	save_file()

