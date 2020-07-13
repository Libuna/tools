#!/home/repos/public/Python/bin/python3.6

#  lipa-devops                  #
#  automation tools development #
#  libor.slavata@cz.verizon.com #

import authentication
import os
import smtplib
import paramiko
from scp import SCPClient
from datetime import date
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from netmiko import NetMikoTimeoutException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

def database_backup__createSSHClient(d_conf):
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(d_conf['vmanage_ip'], 22, d_conf['vmanage_username'], d_conf['vmanage_password'])
	return client

def database_backup__email(message):
	msg = MIMEMultipart()
	msg['Subject'] = message
	msg['From'] = 'viptela_automation@cz.verizon.com'
	msg['To'] = gd_conf['my_email']
	body = "vManage is not accessible. Database backup failed."
	msg.attach(MIMEText(body, 'plain'))
	p = MIMEBase('application', 'octet-stream')
	msg.attach(p)
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()

gs_session, gd_conf = authentication.login()

date = date.today()

s_backup_folder = os.path.isdir(gd_conf['userpath'] + '/viptela/backup')
if not s_backup_folder:
	os.mkdir(gd_conf['userpath'] + '/viptela/backup')
	os.chmod(gd_conf['userpath'] + '/viptela/backup', 0o700)

vmanage = {
	'device_type': 'cisco_ios',
	'host': gd_conf['vmanage_ip'],
	'username': gd_conf['vmanage_username'],
	'password': gd_conf['vmanage_password'],
}


try:
	net_connect = ConnectHandler(**vmanage)

except (NetMikoAuthenticationException):
	print('\n')
	print('Login failed. Please try again.\n')
	message = 'Login failed'
	database_backup__email(message)
	exit()

except (NetMikoTimeoutException):
	print('\n')
	print('IP address not responding.\n')
	message = 'IP address not responding'
	database_backup__email(message)
	exit()

output = net_connect.send_command('request nms configuration-db backup path database_backup_%s'% date)
print('\n')
print(output)
net_connect.disconnect()

try:
	ssh = database_backup__createSSHClient(gd_conf)
	scp = SCPClient(ssh.get_transport())
	scp.get(remote_path='/opt/data/backup/database_backup_%s.tar.gz' % date, local_path=gd_conf['userpath'] + '/viptela/backup/')
	os.chmod(gd_conf['userpath'] + '/viptela/backup/database_backup_%s.tar.gz' % date, 0o700)
	print('\n')
	print("File successfully downloaded ... \n")
except:
	print('\n')
	print("Couldn't connect to sftp or upload failed\n")
	message = "Couldn't connect to sftp or upload failed"
	database_backup__email(message)






